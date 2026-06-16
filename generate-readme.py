#!/usr/bin/env python3
"""
Regenerate README.md from markdown posts in posts/.

Run from the repo root:
    python3 generate-readme.py
"""

import os
import re
from datetime import datetime


def parse_frontmatter(content: str) -> dict[str, str] | None:
    """Extract key-value front matter from a markdown file.

    Returns None if no front matter block is found.
    """
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    frontmatter = {}
    for line in match.group(1).splitlines():
        colon = line.find(":")
        if colon == -1:
            continue
        key = line[:colon].strip()
        value = line[colon + 1 :].strip().strip("'\"")
        frontmatter[key] = value
    return frontmatter


def format_date(date_str: str) -> str:
    """Format an ISO date (YYYY-MM-DD) for the README table, e.g. "May 7, 2026"."""
    date = datetime.strptime(date_str[:10], "%Y-%m-%d")
    return f"{date.strftime('%b')} {date.day}, {date.year}"


def load_posts(posts_dir: str) -> list[dict[str, str]]:
    """Load post metadata from markdown files, sorted newest first."""
    posts = []
    markdown_files = [
        filename for filename in os.listdir(posts_dir)
        if filename.endswith(".md")
    ]
    for filename in markdown_files:
        with open(os.path.join(posts_dir, filename)) as f:
            frontmatter = parse_frontmatter(f.read())
        if frontmatter:
            post = {**frontmatter, "_filename": filename}
            posts.append(post)

    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def posts_link_prefix(posts_dir: str, readme_path: str) -> str:
    """Relative path from the README to the posts directory, for markdown links."""
    return os.path.relpath(posts_dir, os.path.dirname(readme_path)).replace("\\", "/")


def build_readme(
    posts: list[dict[str, str]], preamble: str, posts_link_prefix: str
) -> str:
    """Assemble README markdown from post metadata."""
    rows = []
    for post in posts:
        title = f'[{post["title"]}]({posts_link_prefix}/{post["_filename"]})'
        subtitle = post["subtitle"]
        date = format_date(post["date"])
        row = f'| {date} | {title} | {subtitle} |'
        rows.append(row)

    return "\n".join(
        [
            preamble,
            "",
            "## Articles",
            "",
            "| Date | Title | Subtitle |",
            "|------|-------|----------|",
            "\n".join(rows),
            "",
        ]
    )


def main(posts_dir: str, readme_path: str, preamble: str) -> None:
    """Generate README from posts and write it to readme_path."""
    posts = load_posts(posts_dir)
    link_prefix = posts_link_prefix(posts_dir, readme_path)
    with open(readme_path, "w") as f:
        f.write(build_readme(posts, preamble, link_prefix))
    print(f"{readme_path} written with {len(posts)} articles.")


if __name__ == "__main__":
    root = os.path.dirname(__file__)
    main(
        posts_dir=os.path.join(root, "posts"),
        readme_path=os.path.join(root, "README.md"),
        preamble="A collection of articles by Michael Petrovich on product, engineering, and leadership.",
    )
