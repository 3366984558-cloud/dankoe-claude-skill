"""Clean residual subscribe/nav/duplicate-H1 cruft from already-fetched essays."""
import re
from pathlib import Path

ESSAYS_DIR = Path(__file__).parent.parent / "essays"

# Patterns to strip wherever they appear in the body.
LINE_DROPS = [
    re.compile(r"^Not A Subscriber\??$", re.I),
    re.compile(r"^Join 120,000\+.*$", re.I),
    re.compile(r"^Receive 2 free letters a week\s*$", re.I),
    re.compile(r"^\*\s+Dan Koe\s*$"),
    re.compile(r"^\*\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\s*$"),  # "* May 12, 2021"
]


def clean(text: str) -> str:
    lines = text.splitlines()
    # Find the title line we wrote ourselves: first "# Title" + the "source: ..." pair.
    # Everything between that source line and the SECOND "# " heading is the cruft block.
    if not lines or not lines[0].startswith("# "):
        return text

    our_title = lines[0]
    # Find source line
    src_idx = None
    for i, ln in enumerate(lines[:5]):
        if ln.startswith("source: "):
            src_idx = i
            break
    if src_idx is None:
        return text

    # Find the duplicate H1 (the article's own title heading) somewhere after src_idx.
    dup_idx = None
    for j in range(src_idx + 1, min(src_idx + 25, len(lines))):
        if lines[j].startswith("# "):
            dup_idx = j
            break

    if dup_idx is not None:
        # Drop the cruft (lines between source and duplicate H1) AND the duplicate H1 itself
        body = lines[dup_idx + 1 :]
        header = [our_title, "", lines[src_idx], ""]
    else:
        # No duplicate H1 — just drop matching cruft lines in the first 20 lines
        body = lines[src_idx + 1 :]
        body = [ln for ln in body if not any(p.match(ln.strip()) for p in LINE_DROPS)]
        header = [our_title, "", lines[src_idx], ""]

    # Also drop any stray subscribe lines anywhere in body
    body = [ln for ln in body if not any(p.match(ln.strip()) for p in LINE_DROPS)]

    # Strip leading blank lines from body
    while body and not body[0].strip():
        body.pop(0)

    out = "\n".join(header + body).rstrip() + "\n"
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


def main():
    files = sorted(ESSAYS_DIR.glob("*.md"))
    changed = 0
    for p in files:
        original = p.read_text(encoding="utf-8")
        cleaned = clean(original)
        if cleaned != original:
            p.write_text(cleaned, encoding="utf-8")
            changed += 1
    print(f"cleaned {changed}/{len(files)} files")


if __name__ == "__main__":
    main()
