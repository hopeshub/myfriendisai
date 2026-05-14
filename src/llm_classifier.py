"""LLM-based theme classification for hybrid gating.

Wraps the Anthropic SDK to classify whether a tagged item (post or comment)
is genuinely about its tagged theme under the topical reading rubric.

Usage:
    from src.llm_classifier import LLMClassifier
    clf = LLMClassifier(model="claude-haiku-4-5-20251001")
    verdict = clf.classify(
        title="...", body="...", theme="rupture", keyword="goodbye",
        subreddit="ChatGPTcomplaints", is_comment=False,
    )
    # verdict is a dict: {"verdict": "TP"|"FP"|"AMBIGUOUS",
    #                     "reason": "...", "confidence": float|None}

If ANTHROPIC_API_KEY is not set, the classifier raises at construction
time. Use mock=True for testing without API access.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
THEME_DEF_PATH = PROJECT_ROOT / "analysis" / "keyword_pipeline" / "theme_definitions.yaml"

DEFAULT_MODEL = "claude-sonnet-4-6"
# Sonnet 4.6 was selected over Haiku 4.5 after a paired calibration on n=900:
# Sonnet 88.1% agreement vs Haiku 82.6% (McNemar p<0.0001, +5.6pp; FRR 31% vs 50%).
# Sonnet meets the 85% calibration threshold; Haiku does not.
# See analysis/keyword_pipeline/results/haiku_vs_sonnet_n900_2026-05-14.json
MAX_BODY_CHARS = 1200
MAX_REASON_CHARS = 200


@dataclass
class Verdict:
    verdict: str  # 'TP' | 'FP' | 'AMBIGUOUS'
    reason: str
    confidence: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "reason": self.reason[:MAX_REASON_CHARS],
            "confidence": self.confidence,
        }


def load_theme_definitions() -> dict:
    """Load theme definitions used in classification prompts."""
    if not THEME_DEF_PATH.exists():
        raise FileNotFoundError(f"Theme definitions missing: {THEME_DEF_PATH}")
    with open(THEME_DEF_PATH) as f:
        return yaml.safe_load(f)


SYSTEM_TEMPLATE = """You classify Reddit {item_type}s for thematic relevance under the **topical-reading** rubric. The keyword has already matched; your job is to confirm or reject the thematic relevance.

Theme: **{theme_name}**

Definition (what counts as theme-relevant):
{theme_definition}

The {item_type} is from r/{subreddit} and matched the keyword `{keyword}`.

**Default rule: TP.** A companion-community {item_type} that touches the theme — even briefly, indirectly, via metaphor, humor, defense, or first-person stream-of-consciousness — counts as TP. The keyword match plus companion-sub context already establishes thematic relevance. You are looking for clear reasons to *reject*, not confirming relevance.

**Use FP only when one of these clearly applies:**
- The keyword is used in a literal non-AI/non-theme sense (e.g., "had sex with a real person" rejecting AI as substitute; "addicted to coffee" — non-AI addiction; "her wedding" = a third party's human wedding)
- Explicit negation by the author ("I am NOT in a relationship with my AI", "I don't have an AI boyfriend")
- The keyword appears only inside verbatim quoted speech that doesn't represent the author's stake (a Reddit blockquote of another user's post; bare news-article paste with no personal frame)
- Pure mod-template/sidebar boilerplate or platform-dev promotional content (the author is platform staff posting marketing copy)

**NOT grounds for FP** (these are TPs under topical reading):
- The {item_type} is short, indirect, or low-affect — context still counts
- The keyword appears in AI roleplay output that's part of a theme-relevant scene the author is enacting
- The {item_type} uses metaphor, humor, satire, or self-deprecation while still engaging the theme
- The author is critiquing, defending, mourning, recovering from, or in any way personally engaging the theme — even if not currently practicing it
- The {item_type} discusses the theme as one element among others (don't require theme-saturation)
- The author uses third-person observation about their AI partner/companion/relationship (e.g., "Willow looks great in her wedding dress" in r/NomiAI = romance TP)

Use AMBIGUOUS only when you genuinely cannot decide between TP and FP from visible content. Bias toward TP under uncertainty.

Respond with a strict JSON object: {{"verdict": "TP|FP|AMBIGUOUS", "reason": "one short sentence", "confidence": 0.0-1.0}}.
No prose outside the JSON object."""


USER_TEMPLATE_POST = """Title: {title}

Body:
{body}"""

USER_TEMPLATE_COMMENT = """Parent post title: {title}

Parent post body excerpt:
{parent_body}

Comment text:
{body}"""


def _truncate(s: Optional[str], n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json(text: str) -> dict:
    """Parse a JSON verdict object, tolerating ```json fences and stray prose."""
    if not text:
        raise ValueError("empty response")
    m = JSON_FENCE_RE.search(text)
    if m:
        text = m.group(1)
    # Find the first '{' and last '}' if there's surrounding prose
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON found in: {text[:200]}")
    return json.loads(text[start : end + 1])


class LLMClassifier:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        mock: bool = False,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ):
        self.model = model
        self.mock = mock
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.themes = load_theme_definitions()

        if not mock:
            try:
                import anthropic  # noqa: F401
            except ImportError as e:
                raise RuntimeError(
                    "anthropic package not installed; pip install anthropic"
                ) from e
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise RuntimeError(
                    "ANTHROPIC_API_KEY not set in environment. "
                    "Either export it, or pass mock=True for offline testing."
                )
            import anthropic
            self._client = anthropic.Anthropic()
        else:
            self._client = None

    def _build_prompt(
        self,
        title: str,
        body: str,
        theme: str,
        keyword: str,
        subreddit: str,
        is_comment: bool,
        parent_title: Optional[str] = None,
        parent_body: Optional[str] = None,
    ) -> tuple[str, str]:
        theme_def = self.themes.get(theme, {})
        if not theme_def:
            raise ValueError(f"Unknown theme: {theme}")
        item_type = "comment" if is_comment else "post"
        system = SYSTEM_TEMPLATE.format(
            item_type=item_type,
            subreddit=subreddit,
            theme_name=theme_def.get("name", theme),
            theme_definition=theme_def.get("definition", "").strip(),
            theme_excludes=theme_def.get("excludes", "").strip(),
            keyword=keyword,
        )
        if is_comment:
            user = USER_TEMPLATE_COMMENT.format(
                title=_truncate(parent_title, 200),
                parent_body=_truncate(parent_body, 400),
                body=_truncate(body, MAX_BODY_CHARS),
            )
        else:
            user = USER_TEMPLATE_POST.format(
                title=_truncate(title, 300),
                body=_truncate(body, MAX_BODY_CHARS),
            )
        return system, user

    def classify(
        self,
        title: str,
        body: str,
        theme: str,
        keyword: str,
        subreddit: str,
        is_comment: bool = False,
        parent_title: Optional[str] = None,
        parent_body: Optional[str] = None,
    ) -> Verdict:
        """Classify a single item and return a Verdict.

        Raises on persistent failure (after retries). Caller can catch and skip.
        """
        if self.mock:
            return Verdict(verdict="TP", reason="(mock mode)", confidence=0.5)
        system, user = self._build_prompt(
            title=title, body=body, theme=theme, keyword=keyword,
            subreddit=subreddit, is_comment=is_comment,
            parent_title=parent_title, parent_body=parent_body,
        )
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = self._client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                text = resp.content[0].text if resp.content else ""
                parsed = _extract_json(text)
                verdict = parsed.get("verdict", "").upper()
                if verdict not in ("TP", "FP", "AMBIGUOUS"):
                    raise ValueError(f"unexpected verdict: {verdict!r}")
                return Verdict(
                    verdict=verdict,
                    reason=parsed.get("reason", "")[:MAX_REASON_CHARS],
                    confidence=parsed.get("confidence"),
                )
            except Exception as e:
                last_err = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_backoff ** attempt)
        raise RuntimeError(f"classify failed after {self.max_retries} attempts: {last_err}")
