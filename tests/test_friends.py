import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from friendslib import parse_friend, replace_friend
from generate_data import build_data
from update_feeds import parse_feed


BODY = """Before
```json
{"title":"Example","url":"https://example.com","icon":"","description":"","feed":""}
```
After"""


class FriendsTest(unittest.TestCase):
    def test_issue_json_round_trip(self):
        data = parse_friend(BODY)
        data["description"] = "Changed"
        updated = replace_friend(BODY, data)
        self.assertEqual(parse_friend(updated)["description"], "Changed")
        self.assertTrue(updated.startswith("Before"))
        self.assertTrue(updated.endswith("After"))

    def test_rss_relative_link_becomes_absolute(self):
        xml = b"""<rss version="2.0"><channel><item>
        <title>Post</title><link>/posts/example</link>
        <pubDate>Sun, 28 Jun 2026 03:25:54 GMT</pubDate>
        </item></channel></rss>"""
        posts = parse_feed(xml, "https://blog.example/rss.xml")
        self.assertEqual(posts[0]["link"], "https://blog.example/posts/example")
        self.assertEqual(posts[0]["published"], "2026-06-28 11:25")

    def test_atom(self):
        xml = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <title>Post</title><link href="https://example.com/post"/>
        <updated>2026-06-28T03:25:54Z</updated>
        </entry></feed>"""
        posts = parse_feed(xml, "https://example.com/atom.xml")
        self.assertEqual(posts[0]["link"], "https://example.com/post")

    def test_generator_filters_review_and_sorts_posts(self):
        def issue(number, labels=(), published=""):
            data = parse_friend(BODY)
            if published:
                data["posts"] = [{"title": "Post", "link": "x", "published": published}]
            return {
                "number": number,
                "body": replace_friend(BODY, data),
                "labels": [{"name": label, "color": "ededed"} for label in labels],
            }

        result = build_data(
            [issue(1), issue(2, published="2026-01-01 00:00"), issue(3, ("审核中",))]
        )
        self.assertEqual([item["issue_number"] for item in result["content"]], [2, 1])


if __name__ == "__main__":
    unittest.main()
