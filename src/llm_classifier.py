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

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
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


SYSTEM_TEMPLATE = """You are an adversarial discourse-analysis classifier.

Task: decide whether the given Reddit {item_type} from r/{subreddit} is genuinely about the **{theme_name}** theme under the topical reading.

Theme definition:
{theme_definition}

Excludes (classify FP if these apply):
{theme_excludes}

The {item_type} matched the keyword `{keyword}`. Check whether the keyword's appearance reflects genuine theme content, or whether it's:
- Polysemy (different sense of the same word)
- Negation ("not in a relationship with it")
- Sarcasm / irony
- Quoted speech (quoting another user or AI roleplay output)
- Off-topic content within an on-topic thread
- Metaphorical use without theme content
- Marketing copy or platform-dev promotional content

If genuinely about the theme: verdict TP. If clearly not: verdict FP. If you cannot decide from the visible content: verdict AMBIGUOUS.

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
