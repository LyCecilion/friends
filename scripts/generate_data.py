#!/usr/bin/env python3
"""Generate Stellar friends v2/data.json from approved GitHub Issues."""

from __future__ import annotations

import json
from pathlib import Path

from friendslib import GitHub, label_names, parse_friend, public_label


EXCLUDED_LABELS = {"审核中", "风险网站"}
HIDDEN_LABELS = {"白名单"}


def build_data(issues: list[dict]) -> dict:
    content = []
    for issue in issues:
        if label_names(issue) & EXCLUDED_LABELS:
            continue
        try:
            friend = parse_friend(issue.get("body", ""))
        except (ValueError, json.JSONDecodeError) as error:
            print(f"Skipping issue #{issue['number']}: {error}")
            continue
        friend["issue_number"] = issue["number"]
        friend["labels"] = [
            public_label(label)
            for label in issue.get("labels", [])
            if label["name"] not in HIDDEN_LABELS
        ]
        content.append(friend)

    content.sort(
        key=lambda friend: (
            friend.get("posts", [{}])[0].get("published", "")
            if friend.get("posts")
            else "",
            friend["issue_number"],
        ),
        reverse=True,
    )
    return {"version": "v2", "content": content}


def main() -> None:
    data = build_data(GitHub().open_issues())
    path = Path("v2/data.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {path} with {len(data['content'])} friends")


if __name__ == "__main__":
    main()
