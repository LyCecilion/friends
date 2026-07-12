#!/usr/bin/env python3
"""Maintain the 失联 label for approved friend sites."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from friendslib import GitHub, label_names, parse_friend


EXCLUDED_LABELS = {"审核中", "白名单"}
UNREACHABLE_LABEL = "失联"
USER_AGENT = "CrystaRin-friends/1.0 (+https://crystal.stellalyr.ink/social/)"


def reachable(url: str) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response.read(1)
            return response.status < 500
    except urllib.error.HTTPError as error:
        # Authentication and anti-bot responses still prove that the site is online.
        return error.code < 500
    except Exception as error:
        print(f"Unreachable {url}: {error}")
        return False


def main() -> None:
    github = GitHub()
    for issue in github.open_issues():
        labels = label_names(issue)
        if labels & EXCLUDED_LABELS:
            continue
        try:
            friend = parse_friend(issue.get("body", ""))
        except (ValueError, json.JSONDecodeError) as error:
            print(f"Skipping issue #{issue['number']}: {error}")
            continue
        is_reachable = reachable(friend["url"])
        if is_reachable and UNREACHABLE_LABEL in labels:
            github.remove_label(issue["number"], UNREACHABLE_LABEL)
            print(f"Restored issue #{issue['number']}")
        elif not is_reachable and UNREACHABLE_LABEL not in labels:
            github.add_label(issue["number"], UNREACHABLE_LABEL)
            print(f"Marked issue #{issue['number']} unreachable")
        else:
            print(f"Issue #{issue['number']} unchanged")


if __name__ == "__main__":
    main()
