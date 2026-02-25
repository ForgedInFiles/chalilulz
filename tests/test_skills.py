"""
test_skills — Skill loading, parsing, and prompt generation
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import _parse_frontmatter, _skill_dirs, load_skills, skills_prompt


class TestParseFrontmatter(unittest.TestCase):
    def test_parse_simple_frontmatter(self):
        text = """---
name: test-skill
description: A test skill
---
Skill content here."""
        fm = _parse_frontmatter(text)
        self.assertEqual(fm["name"], "test-skill")
        self.assertEqual(fm["description"], "A test skill")

    def test_parse_no_frontmatter(self):
        text = "Just plain content without frontmatter"
        fm = _parse_frontmatter(text)
        self.assertEqual(fm, {})

    def test_parse_unterminated_frontmatter(self):
        text = """---
name: incomplete
description: Missing closing delimiter
More content"""
        fm = _parse_frontmatter(text)
        self.assertEqual(fm, {})

    def test_parse_extra_fields(self):
        text = """---
name: skill
description: desc
author: John
version: 1.0
---
Content"""
        fm = _parse_frontmatter(text)
        self.assertEqual(fm["name"], "skill")
        self.assertEqual(fm["description"], "desc")
        self.assertEqual(fm["author"], "John")
        self.assertEqual(fm["version"], "1.0")

    def test_parse_whitespace_handling(self):
        text = """---
  name:  spaced  
  description :  test  
---
Content"""
        fm = _parse_frontmatter(text)
        self.assertEqual(fm["name"], "spaced")
        self.assertEqual(fm["description"], "test")


class TestSkillDirs(unittest.TestCase):
    def test_skill_dirs_returns_list(self):
        dirs = _skill_dirs()
        self.assertIsInstance(dirs, list)

    def test_skill_dirs_filters_nonexistent(self):
        # Should only return directories that exist
        dirs = _skill_dirs()
        for d in dirs:
            self.assertTrue(Path(d).is_dir())


class TestLoadSkills(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.test_dir) / ".agents" / "skills"
        self.skills_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_empty_skills_dir(self):
        skills = load_skills()
        # Should not crash, returns list
        self.assertIsInstance(skills, list)

    def test_load_single_skill(self):
        skill_dir = self.skills_dir / "skill-one"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: skill-one
description: First test skill
---
""")
        # Temporarily add our test dir to the search path by monkey-patching
        import chalilulz

        orig_skill_dirs = chalilulz._skill_dirs

        def mock_skill_dirs():
            return [self.skills_dir]

        chalilulz._skill_dirs = mock_skill_dirs
        try:
            skills = load_skills()
            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0]["name"], "skill-one")
            self.assertEqual(skills[0]["desc"], "First test skill")
        finally:
            chalilulz._skill_dirs = orig_skill_dirs

    def test_load_multiple_skills(self):
        skill1 = self.skills_dir / "skill-one"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text("""---
name: skill-one
description: First skill
---
""")
        skill2 = self.skills_dir / "skill-two"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text("""---
name: skill-two
description: Second skill
---
""")
        import chalilulz

        orig_skill_dirs = chalilulz._skill_dirs

        def mock_skill_dirs():
            return [self.skills_dir]

        chalilulz._skill_dirs = mock_skill_dirs
        try:
            skills = load_skills()
            self.assertEqual(len(skills), 2)
            names = [s["name"] for s in skills]
            self.assertIn("skill-one", names)
            self.assertIn("skill-two", names)
        finally:
            chalilulz._skill_dirs = orig_skill_dirs

    def test_load_skill_with_extra_scripts_dir(self):
        skill_dir = self.skills_dir / "skill-with-scripts"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: skill-with-scripts
description: Has scripts
---
""")
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "test.py").write_text("print('hello')")
        import chalilulz

        orig_skill_dirs = chalilulz._skill_dirs

        def mock_skill_dirs():
            return [self.skills_dir]

        chalilulz._skill_dirs = mock_skill_dirs
        try:
            skills = load_skills()
            self.assertEqual(len(skills), 1)
            # load_skills only returns name/desc/path, not scripts
        finally:
            chalilulz._skill_dirs = orig_skill_dirs

    def test_load_skill_missing_name_description(self):
        skill_dir = self.skills_dir / "bad_skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
author: Unknown
---
No name or description""")
        import chalilulz

        orig_skill_dirs = chalilulz._skill_dirs

        def mock_skill_dirs():
            return [self.skills_dir]

        chalilulz._skill_dirs = mock_skill_dirs
        try:
            skills = load_skills()
            # Should skip skills without name+description
            self.assertEqual(len(skills), 0)
        finally:
            chalilulz._skill_dirs = orig_skill_dirs

    def test_load_skills_prevents_duplicates(self):
        skill_dir = self.skills_dir / "duplicate-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("""---
name: duplicate-skill
description: Same skill
---
""")
        # Add same skills dir twice (simulate multiple search paths)
        import chalilulz

        orig_skill_dirs = chalilulz._skill_dirs

        def mock_skill_dirs():
            return [self.skills_dir, self.skills_dir]  # duplicate

        chalilulz._skill_dirs = mock_skill_dirs
        try:
            skills = load_skills()
            # Should appear only once
            self.assertEqual(len(skills), 1)
        finally:
            chalilulz._skill_dirs = orig_skill_dirs


class TestSkillsPrompt(unittest.TestCase):
    def test_skills_prompt_empty(self):
        result = skills_prompt([])
        self.assertEqual(result, "")

    def test_skills_prompt_with_skills(self):
        skills = [
            {"name": "skill1", "desc": "Description one"},
            {"name": "skill2", "desc": "Description two longer"},
        ]
        result = skills_prompt(skills)
        self.assertIn("Available Skills", result)
        self.assertIn("skill1", result)
        self.assertIn("Description one", result)
        self.assertIn("skill2", result)
        self.assertIn("load_skill", result)

    def test_skills_prompt_truncates_long_desc(self):
        long_desc = "A" * 200
        skills = [{"name": "long", "desc": long_desc}]
        result = skills_prompt(skills)
        # Should be truncated to 120 characters in the description part
        # The result should contain the name and exactly 120 'A's (or less if not enough)
        self.assertIn("long", result)
        # Check that the description part is at most 120 characters (plus name and colon)
        lines = result.strip().split("\n")
        skill_line = lines[1]  # first line after header
        # Extract description part after ": "
        parts = skill_line.split(": ", 1)
        self.assertEqual(len(parts), 2)
        desc_part = parts[1]
        self.assertLessEqual(len(desc_part), 120)


if __name__ == "__main__":
    unittest.main()
