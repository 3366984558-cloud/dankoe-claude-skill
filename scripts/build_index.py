"""Build a paragraph-level keyword index for all dankoe corpus files.

Scans:
- essays/*.md         (Dan Koe's letters, scraped)
- frameworks/*.md     (hand-written framework summaries)
- transcripts/*.md    (YouTube transcripts, optional)
- quotes.md           (curated quotes)

Output: index.json containing a list of paragraphs with metadata + token freq.
"""
import json
import re
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
INDEX_FILE = SKILL_DIR / "index.json"

CORPUS_DIRS = ["essays", "frameworks", "transcripts"]
EXTRA_FILES = ["quotes.md", "voice.md"]

# English stopwords (small list - keep it lean)
STOPWORDS = set("""
a an the of and or but in on at to for from with by as is are was were be been being have has had
do does did done will would shall should can could may might must
i you he she it we they me him her us them my your his its our their this that these those
what who whom which when where why how if so not no yes do don dont not
about above after again against all am also any because before below between both each few
further here how more most much none nor of off once only other out over own same such than
then there through too under until up very very
""".split())

# Chinese-English synonym map (loose - extended in search.py)
CN_EN_SYNONYMS = {
    "一人公司": "one-person business solopreneur",
    "个人品牌": "personal brand",
    "数字杠杆": "digital leverage",
    "杠杆": "leverage",
    "使命": "purpose",
    "意义": "meaning purpose",
    "纪律": "discipline",
    "自律": "self-discipline discipline",
    "心流": "flow state",
    "受众": "audience",
    "粉丝": "audience followers",
    "变现": "monetize monetization money income",
    "赚钱": "money rich monetize income",
    "定价": "pricing price product",
    "写作": "writing write content",
    "内容": "content writing",
    "创作": "create creator creative",
    "创作者": "creator",
    "技能": "skill",
    "技能栈": "skill stack",
    "副业": "side-hustle business income",
    "焦虑": "anxiety overwhelm lost",
    "迷茫": "lost uncertainty rut",
    "拖延": "procrastination procrastinate",
    "深度工作": "deep work focus",
    "专注": "focus concentration",
    "习惯": "habit habits",
    "目标": "goal goals",
    "AI": "ai artificial intelligence",
    "GPT": "ai gpt",
    "成长": "growth grow",
    "改变": "change reinvent",
    "重塑": "reinvent rebuild",
    "目的": "purpose meaning",
    "焦点": "focus",
    "草根": "underdog scratch zero",
    "起步": "start scratch zero beginner",
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-zA-Z]+|[一-鿿]+", text)
    out = []
    for t in tokens:
        if re.match(r"[一-鿿]+", t):
            out.extend([c for c in t if "一" <= c <= "鿿"])
        else:
            if len(t) >= 2 and t not in STOPWORDS:
                out.append(t)
    return out


def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if len(p.strip()) >= 40]


def collect_files() -> list[Path]:
    files = []
    for d in CORPUS_DIRS:
        files.extend((SKILL_DIR / d).glob("*.md"))
    for f in EXTRA_FILES:
        p = SKILL_DIR / f
        if p.exists():
            files.append(p)
    return files


def main():
    files = collect_files()
    print(f"[build_index] scanning {len(files)} files")

    entries = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  skip {f.name}: {e}")
            continue

        source = ""
        m = re.search(r"^source:\s*(\S+)", text, re.M)
        if m:
            source = m.group(1)

        title = ""
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            title = m.group(1).strip()

        rel = str(f.relative_to(SKILL_DIR)).replace("\\", "/")

        for i, p in enumerate(split_paragraphs(text)):
            tokens = tokenize(p)
            if not tokens:
                continue
            freq = Counter(tokens)
            entries.append({
                "file": rel,
                "title": title,
                "source": source,
                "para_idx": i,
                "text": p,
                "freq": dict(freq),
                "len": len(tokens),
            })

    # Document frequency for IDF
    df = Counter()
    for e in entries:
        for tok in e["freq"]:
            df[tok] += 1

    payload = {
        "entries": entries,
        "df": dict(df),
        "n_docs": len(entries),
        "synonyms": CN_EN_SYNONYMS,
    }
    INDEX_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"[build_index] {len(entries)} paragraphs indexed -> {INDEX_FILE} ({INDEX_FILE.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
