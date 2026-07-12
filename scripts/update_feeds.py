#!/usr/bin/env python3
"""Fetch approved friends' RSS/Atom feeds and update their Issue JSON."""

from __future__ import annotations

import datetime as dt
import email.utils
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from friendslib import GitHub, label_names, parse_friend, replace_friend


EXCLUDED_LABELS = {"审核中", "风险网站"}
USER_AGENT = "CrystaRin-friends/1.0 (+https://crystal.stellalyr.ink/social/)"


def text(element, path: str) -> str:
    child = element.find(path)
    return (child.text or "").strip() if child is not None else ""


def normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except ValueError:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")


def parse_feed(xml: bytes, feed_url: str, limit: int = 3) -> list[dict]:
    root = ET.fromstring(xml)
    posts = []
    if root.tag.rsplit("}", 1)[-1].lower() == "rss":
        entries = root.findall("./channel/item")
        for entry in entries:
            link = text(entry, "link") or text(entry, "guid")
            posts.append(
                {
                    "title": text(entry, "title"),
                    "link": urllib.parse.urljoin(feed_url, link),
                    "published": normalize_date(text(entry, "pubDate")),
                }
            )
    else:
        entries = root.findall("{*}entry")
        for entry in entries:
            link = ""
            for candidate in entry.findall("{*}link"):
                if candidate.get("rel", "alternate") == "alternate":
                    link = candidate.get("href", "")
                    break
            posts.append(
                {
                    "title": text(entry, "{*}title"),
                    "link": urllib.parse.urljoin(feed_url, link),
                    "published": normalize_date(
                        text(entry, "{*}published") or text(entry, "{*}updated")
                    ),
                }
            )
    return [post for post in posts if post["title"] and post["link"]][:limit]


def fetch_feed(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    github = GitHub()
    for issue in github.open_issues():
        if label_names(issue) & EXCLUDED_LABELS:
            continue
        try:
            friend = parse_friend(issue.get("body", ""))
        except (ValueError, json.JSONDecodeError) as error:
            print(f"Skipping issue #{issue['number']}: {error}")
            continue
        feed = friend.get("feed", "").strip()
        if not feed:
            continue
        try:
            posts = parse_feed(fetch_feed(feed), feed)
        except Exception as error:
            print(f"Feed failed for issue #{issue['number']}: {error}")
            continue
        if friend.get("posts") == posts:
            print(f"Issue #{issue['number']} is current")
            continue
        friend["posts"] = posts
        github.update_issue_body(issue["number"], replace_friend(issue["body"], friend))
        print(f"Updated issue #{issue['number']} with {len(posts)} posts")


if __name__ == "__main__":
    main()
