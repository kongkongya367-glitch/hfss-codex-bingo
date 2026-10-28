"""Check reusable skill links and Python syntax without executing automation."""
import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_skill_entrypoint_and_invocation_exist(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: hfss-codex-bingo", text)
        ui = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$hfss-codex-bingo", ui)

    def test_local_markdown_links_resolve(self):
        for file in [ROOT / "SKILL.md", ROOT / "README.md", *(ROOT / "references").glob("*.md")]:
            with self.subTest(file=file.name):
                for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = link.split("#", 1)[0]
                    if target:
                        self.assertTrue((file.parent / target).exists(), (file, target))

    def test_helper_sources_parse_without_hfss(self):
        for file in (ROOT / "scripts").glob("*.py"):
            with self.subTest(file=file.name):
                ast.parse(file.read_text(encoding="utf-8"), filename=str(file))


if __name__ == "__main__":
    unittest.main()
