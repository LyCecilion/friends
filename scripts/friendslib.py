#!/usr/bin/env python3
"""Shared helpers for the friends repository automation."""

from __future__ import annotations

import colorsys
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


JSON_BLOCK = re.compile(r"```json\s*\n(?P<data>.*?)\n```", re.DOTALL | re.IGNORECASE)


class GitHub:
    def __init__(self) -> None:
        self.repository = os.environ["GITHUB_REPOSITORY"]
        self.token = os.environ["GITHUB_TOKEN"]
        self.base = f"https://api.github.com/repos/{self.repository}"

    def request(self, method: str, path: str, payload=None):
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "CrystaRin-friends",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode()
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base}{path}", data=data, headers=headers, method=method
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
        return json.loads(content) if content else None

    def open_issues(self):
        issues = []
        page = 1
        while True:
            response = self.request(
                "GET", f"/issues?state=open&per_page=100&page={page}&sort=created&direction=desc"
            )
            batch = [issue for issue in response if "pull_request" not in issue]
            issues.extend(batch)
            if len(response) < 100:
                return issues
            page += 1

    def update_issue_body(self, number: int, body: str) -> None:
        self.request("PATCH", f"/issues/{number}", {"body": body})

    def add_label(self, number: int, label: str) -> None:
        self.request("POST", f"/issues/{number}/labels", {"labels": [label]})

    def remove_label(self, number: int, label: str) -> None:
        encoded = urllib.parse.quote(label, safe="")
        try:
            self.request("DELETE", f"/issues/{number}/labels/{encoded}")
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise


def parse_friend(body: str) -> dict:
    match = JSON_BLOCK.search(body or "")
    if not match:
        raise ValueError("missing JSON code block")
    data = json.loads(match.group("data"))
    if not isinstance(data, dict):
        raise ValueError("friend data must be a JSON object")
    for field in ("title", "url", "icon", "description", "feed"):
        data.setdefault(field, "")
    return data


def replace_friend(body: str, data: dict) -> str:
    replacement = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
    updated, count = JSON_BLOCK.subn(replacement, body or "", count=1)
    if count != 1:
        raise ValueError("missing JSON code block")
    return updated


def label_names(issue: dict) -> set[str]:
    return {label["name"] for label in issue.get("labels", [])}


def public_label(label: dict) -> dict:
    color = label.get("color") or "000000"
    red, green, blue = (int(color[index : index + 2], 16) / 255 for index in (0, 2, 4))
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return {
        "name": label["name"],
        "color": color,
        "hue": round(hue * 360),
        "saturation": round(saturation * 100),
        "lightness": round(lightness * 100),
    }
