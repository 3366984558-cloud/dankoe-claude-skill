"""Fetch all Dan Koe essays from thedankoe.com and save as markdown."""
import os
import re
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
ESSAYS_DIR = SKILL_DIR / "essays"
URLS_FILE = SCRIPT_DIR / "urls.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def fetch_one(url: str) -> tuple[str, str | None, str | None]:
    """Fetch one essay. Returns (slug, markdown_content, error)."""
    slug = slug_from_url(url)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        title_tag = soup.find("h1") or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else slug

        article = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=re.compile(r"(post|content|entry)"))
        )
        if article is None:
            return slug, None, "no article container"

        for bad in article.find_all(["script", "style", "nav", "footer", "aside", "form"]):
            bad.decompose()
        for bad in article.find_all(class_=re.compile(r"(share|subscribe|related|comment|sidebar|newsletter|cta)", re.I)):
            bad.decompose()

        md = markdownify(str(article), heading_style="ATX", strip=["a"]).strip()
        md = re.sub(r"\n{3,}", "\n\n", md)

        full = f"# {title}\n\nsource: {url}\n\n{md}\n"
        return slug, full, None
    except Exception as e:
        return slug, None, str(e)


def main():
    ESSAYS_DIR.mkdir(parents=True, exist_ok=True)
    urls = [line.strip() for line in URLS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[fetch_all] {len(urls)} URLs queued -> {ESSAYS_DIR}")

    existing = {p.stem for p in ESSAYS_DIR.glob("*.md")}
    todo = [u for u in urls if slug_from_url(u) not in existing]
    print(f"[fetch_all] {len(existing)} cached, {len(todo)} to fetch")
    if not todo:
        return

    ok = 0
    fail = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_one, u): u for u in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            slug, md, err = fut.result()
            if err:
                fail.append((slug, err))
                print(f"  [{i}/{len(todo)}] FAIL {slug}: {err}")
            else:
                (ESSAYS_DIR / f"{slug}.md").write_text(md, encoding="utf-8")
                ok += 1
                print(f"  [{i}/{len(todo)}] OK   {slug} ({len(md)} chars)")

    print(f"\n[fetch_all] done. ok={ok} fail={len(fail)}")
    if fail:
        print("Failures:")
        for slug, err in fail:
            print(f"  {slug}: {err}")


if __name__ == "__main__":
    main()
