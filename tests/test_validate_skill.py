import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate_skill.py"
spec = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
validate_skill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_skill)


class ParseFrontmatterTest(unittest.TestCase):
    def test_single_line_description(self):
        fields = validate_skill.parse_frontmatter(
            "---\nname: code-review\ndescription: one line\n---\n# Body\n")
        self.assertEqual(fields["description"], "one line")

    def test_block_scalar_description_is_read_in_full(self):
        text = ("---\n"
                "name: code-review\n"
                "description: >-\n"
                "  Rigorous, prioritized code review of a diff,\n"
                "  PR, or file.\n"
                "version: 1.0.0\n"
                "---\n")
        fields = validate_skill.parse_frontmatter(text)
        self.assertEqual(fields["description"],
                         "Rigorous, prioritized code review of a diff, PR, or file.")
        self.assertEqual(fields["version"], "1.0.0")

    def test_nested_key_does_not_override_top_level(self):
        text = "---\nname: code-review\nmetadata:\n  name: other\n---\n"
        self.assertEqual(validate_skill.parse_frontmatter(text)["name"],
                         "code-review")


if __name__ == "__main__":
    unittest.main()
