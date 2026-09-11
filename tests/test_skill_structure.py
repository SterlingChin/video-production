"""Check this repository's simple frontmatter and bundled file references.

These checks intentionally support our single-line strings and metadata map,
not arbitrary YAML. The Agent Skills specification remains authoritative.
"""

import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


SKILL = Path(__file__).resolve().parents[1] / "skills" / "video-production"


class SkillStructureTests(unittest.TestCase):
    def read_string(self, raw):
        self.assertTrue(raw, "Frontmatter values must be nonempty strings")
        if raw.startswith('"'):
            value = json.loads(raw)
            self.assertIsInstance(value, str)
            return value
        if raw.startswith("'"):
            self.assertTrue(raw.endswith("'"), "Unclosed quoted frontmatter string")
            return raw[1:-1].replace("''", "'")
        self.assertNotRegex(raw, r"^(?:[-+]?\d|[\[\]{}&*!|>@`])",
                            "Quote numeric-looking or special YAML values")
        self.assertNotIn(raw.lower(), {"null", "true", "false", "yes", "no", "on", "off", "~"})
        return raw

    def test_public_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertEqual(lines[0], "---")
        self.assertIn("---", lines[1:], "Frontmatter must have a closing delimiter")
        end = lines.index("---", 1)
        fields, metadata = {}, {}
        in_metadata = False
        for line in lines[1:end]:
            if line == "metadata:":
                self.assertNotIn("metadata", fields, "Duplicate metadata mapping")
                fields["metadata"] = metadata
                in_metadata = True
                continue
            match = re.fullmatch(r"(  )?([a-z][a-z0-9-]*): (.+)", line)
            self.assertIsNotNone(match, f"Keep frontmatter in the documented simple string format: {line}")
            indent, key, raw = match.groups()
            if indent:
                self.assertTrue(in_metadata, "Indented values must belong to metadata")
                target = metadata
            else:
                in_metadata = False
                target = fields
            self.assertNotIn(key, target, f"Duplicate frontmatter key: {key}")
            target[key] = self.read_string(raw)
        self.assertTrue({"name", "description", "license", "metadata"} <= fields.keys())
        self.assertFalse(fields.keys() - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
        self.assertEqual(fields["name"], SKILL.name)
        self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertTrue(1 <= len(fields["description"]) <= 1024)
        if "compatibility" in fields:
            self.assertTrue(1 <= len(fields["compatibility"]) <= 500)
        self.assertEqual(fields["license"], "MIT")
        self.assertTrue(metadata, "Keep author/version metadata with the public skill")
        self.assertTrue(all(isinstance(value, str) and value.strip() for value in metadata.values()))
        self.assertTrue("\n".join(lines[end + 1:]).strip(), "The skill must include instructions")

    def assert_bundled_file(self, source, reference, base):
        path = (base / unquote(reference)).resolve()
        self.assertTrue(path.is_relative_to(SKILL), f"{source}: reference escapes the distributed skill: {reference}")
        self.assertTrue(path.is_file(), f"{source}: missing bundled reference: {reference}")

    def test_relative_markdown_and_helper_references_exist(self):
        for source in SKILL.rglob("*.md"):
            text = source.read_text(encoding="utf-8")
            for link in re.findall(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
                url = urlsplit(link.strip("<>"))
                if not url.scheme and not url.netloc and url.path:
                    with self.subTest(source=source.relative_to(SKILL), link=link):
                        self.assert_bundled_file(source, url.path, source.parent)
            # Commands document helper paths relative to the loaded skill root.
            for reference in re.findall(r"`((?:scripts|references)/[^`\s]+)`", text):
                with self.subTest(source=source.relative_to(SKILL), reference=reference):
                    self.assert_bundled_file(source, reference, SKILL)


if __name__ == "__main__":
    unittest.main()
