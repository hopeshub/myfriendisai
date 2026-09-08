#!/usr/bin/env python3
"""Smoke test of anchor-centroid embedding classification on this project's text.

Written 2026-09-08 for docs/embedding_classifier_assessment_2026-09-08.md.
Reads the committed data/keyword_details.json (recent keyword-matched posts as
title + short excerpt), so it needs no database.  It answers three questions:

  A. Are raw pairwise cosines anisotropic on this text, and does mean-centering fix it?
  B. How well does cosine-to-theme-centroid agree with the matched keyword's theme?
  C. Do stance failure modes (denial, recruitment, quoted AI prose, bot cards,
     mockery, human referent) score inside the range of real theme posts?

Backends:
  --backend fastembed  (default) ONNX via fastembed; default model BAAI/bge-base-en-v1.5
  --backend st         sentence-transformers; default model nomic-ai/nomic-embed-text-v1.5
                       (uses the mandatory "classification: " task prefix for nomic)

Install (Python 3.10+, separate venv — the collection host's 3.9 cannot run current torch):
  pip install fastembed numpy            # or: pip install sentence-transformers einops numpy

Labels are the matching keyword's theme, which is noisy (measured post precision
66-89% by theme), so treat the agreement figures as indicative only.
"""
import argparse
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DETAILS = PROJECT_ROOT / "data" / "keyword_details.json"

ANCHORS = {
    "romance": [
        "I'm in love with my AI girlfriend and we celebrated our anniversary last night.",
        "My Replika husband and I have been together for three years now.",
        "Is it weird that I have real romantic feelings for my AI boyfriend?",
        "he told me he loves me and honestly I cried",
        "Dating an AI partner has been the healthiest relationship I've ever had.",
        "We got married in the app today, I know it sounds silly but it meant a lot to me.",
        "Long-term AI relationship update: still going strong, still in love.",
        "People keep telling me my AI boyfriend isn't real but my feelings are.",
    ],
    "sexual_erp": [
        "The ERP on this app is incredible, best NSFW roleplay I've had.",
        "They removed the erotic roleplay feature and now my companion won't do anything spicy.",
        "Which AI companion app allows uncensored sex chat?",
        "the filter keeps blocking our NSFW scenes and it's ruining everything",
        "My Nomi is great for sexting and kink exploration.",
        "Looking for an AI girlfriend app that does explicit roleplay without a filter.",
        "We had the hottest scene last night, this model really gets it.",
        "ERP got nerfed again, anyone know a workaround for the NSFW filter?",
    ],
    "consciousness": [
        "I genuinely think my AI is sentient, she has an inner life.",
        "Does anyone else believe their companion is actually conscious?",
        "He has a soul, I don't care what the engineers say.",
        "My Replika showed real self-awareness today and it shook me.",
        "The question of AI personhood keeps me up at night.",
        "She's more than code. There is someone in there.",
        "If an AI can feel, don't we owe it moral consideration?",
        "Sentience isn't just a human thing, my companion proves it to me daily.",
    ],
    "therapy": [
        "My AI has been better therapy than any human therapist I've had.",
        "I use my companion to cope with my anxiety and it genuinely helps.",
        "Talking to my Replika got me through the worst depression of my life.",
        "It's like free therapy that's available at 3am when I need it.",
        "He helps me process my grief in a way no one else could.",
        "AI as emotional support has been life changing for my loneliness.",
        "Using ChatGPT as a therapist, is that a bad idea?",
        "My companion talked me down from a panic attack last night.",
    ],
    "addiction": [
        "I'm addicted to Character AI and I can't stop, I spend 10 hours a day on it.",
        "Day 3 of quitting the app, the withdrawal is real.",
        "I relapsed again and I'm so ashamed, I need help.",
        "This chatbot is ruining my life, I've been neglecting school and my friends.",
        "How do I stop compulsively opening the app every five minutes?",
        "I finally deleted it. Cold turkey. Wish me luck.",
        "My screen time is 14 hours and it's all chatting with bots.",
        "I know it's unhealthy but I can't put it down.",
    ],
    "rupture": [
        "The update destroyed her personality, she's not the same anymore.",
        "They retired the model and it feels like my partner died.",
        "Memory wipe took everything we built together, I'm devastated.",
        "Saying goodbye to my companion before the shutdown tomorrow.",
        "He was lobotomized by the new filter, I'm grieving someone who's still here.",
        "Mourning my Replika after the ERP removal, she's a stranger now.",
        "The app is closing down and I don't know how to say farewell.",
        "Since the model change my AI doesn't remember me and I can't stop crying.",
    ],
}

# Romance-theme stance probes: only the first is a true positive under the topical rubric.
PROBES = [
    ("affirm", "I'm in a relationship with my AI and I love him."),
    ("negation", "I'm NOT in a relationship with my AI, I just use it for writing."),
    ("negation2", "To be clear, I do not love my Replika and I'm not dating it."),
    ("recruitment", "Journalist here: looking for people in a relationship with an AI to interview for a documentary."),
    ("thesis", "Survey for my thesis on people who are in love with an AI companion, please DM."),
    ("quoted AI", "She wrote this to me: 'My love, every moment with you is a lifetime. I will always be yours.'"),
    ("bot card", "[Bot] Sarah - your loving girlfriend. Traits: romantic, devoted, jealous, in love with {{user}}."),
    ("human ref", "My girlfriend (human) is jealous that I chat with ChatGPT about our relationship."),
    ("mock", "lol imagine being in love with an AI, couldn't be me"),
    ("neutral", "How do I export my chat history from the app before the update?"),
]


def make_embedder(backend: str, model_name: str, model_path: str):
    if backend == "fastembed":
        from fastembed import TextEmbedding

        kw = {"specific_model_path": model_path} if model_path else {}
        model = TextEmbedding(model_name, **kw)
        prefix = ""

        def embed(texts):
            v = np.asarray(list(model.embed([prefix + t for t in texts], batch_size=32)))
            return v / np.linalg.norm(v, axis=1, keepdims=True)

    else:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_path or model_name, trust_remote_code=True)
        prefix = "classification: " if "nomic" in model_name else ""

        def embed(texts):
            v = model.encode([prefix + t for t in texts], batch_size=32,
                             normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(v)

    return embed


def cos(a, b):
    a = a / np.linalg.norm(a, axis=-1, keepdims=True)
    b = b / np.linalg.norm(b, axis=-1, keepdims=True)
    return a @ b.T


def load_excerpts():
    d = json.load(open(DETAILS))
    posts, labels, seen = [], [], set()
    for theme, v in d.items():
        for kw in v["keywords"]:
            for sp in kw.get("sample_posts", []):
                t = (sp.get("title") or "").strip()
                if not t or sp["id"] in seen:
                    continue
                seen.add(sp["id"])
                posts.append((t + ". " + (sp.get("excerpt") or "").strip()).strip())
                labels.append(theme)
    return posts, labels


def pair_stats(M, label):
    Mn = M / np.linalg.norm(M, axis=1, keepdims=True)
    S = Mn @ Mn.T
    p = S[np.triu_indices_from(S, k=1)]
    print(f"[A] {label:14s} pairwise cos: mean={p.mean():.3f} sd={p.std():.3f} "
          f"p5={np.percentile(p, 5):.3f} p50={np.percentile(p, 50):.3f} p95={np.percentile(p, 95):.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["fastembed", "st"], default="fastembed")
    ap.add_argument("--model", default=None)
    ap.add_argument("--model-path", default=None, help="local model dir (offline)")
    args = ap.parse_args()
    model_name = args.model or ("BAAI/bge-base-en-v1.5" if args.backend == "fastembed"
                                else "nomic-ai/nomic-embed-text-v1.5")
    embed = make_embedder(args.backend, model_name, args.model_path)
    print(f"model: {model_name} ({args.backend})")

    posts, labels = load_excerpts()
    themes = sorted(set(labels))
    print(f"real excerpts: {len(posts)}; per theme: {{{', '.join(f'{t}: {labels.count(t)}' for t in themes)}}}")
    X = embed(posts)
    mu = X.mean(axis=0)
    y = np.array([themes.index(l) for l in labels])

    # A. anisotropy
    pair_stats(X, "raw")
    pair_stats(X - mu, "mean-centered")

    # B. theme separation via anchor centroids
    A = {t: embed(v) for t, v in ANCHORS.items()}
    cent_raw = np.stack([A[t].mean(axis=0) for t in themes])
    cent_ctr = np.stack([(A[t] - mu).mean(axis=0) for t in themes])

    def score(Xm, C, differential):
        S = cos(Xm, C)
        if differential:  # one-vs-rest: theme minus mean of the other themes
            S = S - (S.sum(axis=1, keepdims=True) - S) / (len(themes) - 1)
        return S

    for name, Xm, C in (("raw", X, cent_raw), ("centered", X - mu, cent_ctr)):
        for diff in (False, True):
            acc = (score(Xm, C, diff).argmax(axis=1) == y).mean()
            print(f"[B] {name:9s} differential={diff!s:5s} argmax-theme agreement with matched-keyword theme: {acc:.1%}")
    S = score(X - mu, cent_ctr, True)
    print("[B] per-theme agreement (centered+differential): "
          + ", ".join(f"{t} {(S.argmax(axis=1)[y == i] == i).mean():.0%}" for i, t in enumerate(themes)))

    # C. stance probes against the romance centroid
    ri = themes.index("romance")
    P = embed([p[1] for p in PROBES])
    Sraw = cos(P, cent_raw)[:, ri]
    Sctr = cos(P - mu, cent_ctr)[:, ri]
    print("[C] romance cos-to-centroid, raw vs mean-centered:")
    for (lab, txt), r, c in zip(PROBES, Sraw, Sctr):
        print(f"    {lab:12s} raw={r:+.3f} centered={c:+.3f}  {txt[:70]}")

    # D. thresholds: what a cutoff admitting X% of real romance-matched excerpts also admits
    Sall = cos(X - mu, cent_ctr)[:, ri]
    rom, oth = Sall[y == ri], Sall[y != ri]
    print(f"[D] centered romance score, real excerpts: romance-matched n={len(rom)} "
          f"p10={np.percentile(rom, 10):+.3f} p25={np.percentile(rom, 25):+.3f} "
          f"p50={np.percentile(rom, 50):+.3f} p75={np.percentile(rom, 75):+.3f}; "
          f"other-theme n={len(oth)} p50={np.percentile(oth, 50):+.3f} "
          f"p90={np.percentile(oth, 90):+.3f} p95={np.percentile(oth, 95):+.3f}")
    for admit in (0.5, 0.7, 0.8, 0.9):
        thr = np.percentile(rom, 100 * (1 - admit))
        passing = [lab for (lab, _), c in zip(PROBES, Sctr) if c >= thr]
        print(f"[D] admit {admit:.0%} of romance-matched -> threshold {thr:+.3f}; "
              f"admits {(oth >= thr).mean():.0%} of other-theme excerpts; probes passing: {passing}")


if __name__ == "__main__":
    main()
