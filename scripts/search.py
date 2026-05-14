"""Search the dankoe corpus by keyword query (中英双语 supported).

Usage:
  python search.py "your query"
  python search.py "your query" --top 8 --max-chars 600

Output: JSON to stdout, top-N paragraphs ranked by BM25-lite score.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
INDEX_FILE = SCRIPT_DIR.parent / "index.json"


def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]+|[一-鿿]+", text)
    out = []
    for t in tokens:
        if re.match(r"[一-鿿]+", t):
            out.extend([c for c in t if "一" <= c <= "鿿"])
        else:
            if len(t) >= 2:
                out.append(t)
    return out


def expand_query(query: str, synonyms: dict) -> list[str]:
    """Expand query with synonyms (chinese-english bridging)."""
    expanded = [query]
    for cn, en in synonyms.items():
        if cn in query:
            expanded.append(en)
    return tokenize(" ".join(expanded))


def bm25_score(q_tokens, e, df, n_docs, avg_len, k1=1.5, b=0.75):
    score = 0.0
    freq = e["freq"]
    doc_len = e["len"]
    for t in q_tokens:
        if t not in freq:
            continue
        f = freq[t]
        idf = math.log((n_docs - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5) + 1)
        denom = f + k1 * (1 - b + b * doc_len / avg_len)
        score += idf * (f * (k1 + 1)) / denom
    return score


def search(query: str, top: int = 5, max_chars: int = 600):
    if not INDEX_FILE.exists():
        return {"error": f"index missing at {INDEX_FILE}. Run build_index.py first."}

    payload = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    entries = payload["entries"]
    df = payload["df"]
    n_docs = payload["n_docs"]
    synonyms = payload.get("synonyms", {})
    avg_len = sum(e["len"] for e in entries) / max(1, len(entries))

    q_tokens = expand_query(query, synonyms)
    if not q_tokens:
        return {"error": "empty query after tokenization"}

    q_freq = Counter(q_tokens)
    scored = []
    for e in entries:
        s = bm25_score(list(q_freq.keys()), e, df, n_docs, avg_len)
        if s > 0:
            scored.append((s, e))

    scored.sort(key=lambda x: -x[0])
    hits = []
    for s, e in scored[:top]:
        text = e["text"]
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        hits.append({
            "score": round(s, 3),
            "file": e["file"],
            "title": e["title"],
            "source": e["source"],
            "text": text,
        })

    return {"query": query, "tokens": q_tokens, "n_hits": len(hits), "hits": hits}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="search query (中英文都支持)")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--max-chars", type=int, default=600)
    args = ap.parse_args()

    result = search(args.query, top=args.top, max_chars=args.max_chars)
    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
