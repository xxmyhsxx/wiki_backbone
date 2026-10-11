"""Exercise the public CLI against temporary Wikis, without third-party packages."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_wiki.py"


class WikiLintTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "wiki-root"
        self.root.mkdir()
        for name, text in {
            "README.md": "# Template\n[Wiki](wiki/INDEX.md)\n",
            "AGENTS.md": "# Agent\n",
            "raw/README.md": "# Sources\n",
            "wiki/README.md": "# Rules\n",
            "wiki/SELF.md": "# Self\n",
            "wiki/INDEX.md": "# Index\n",
        }.items():
            self.write(name, text)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        return path

    def cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), *arguments],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def check(self, *arguments):
        result = self.cli(*arguments)
        self.assertNotEqual(result.returncode, 2, result.stderr)
        self.assertFalse(result.stderr, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def test_empty_template_is_valid_deterministic_and_read_only(self):
        before = self.snapshot()
        first = self.cli()
        second = self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(report["summary"]["documents_checked"], 6)
        self.assertEqual(report["summary"]["knowledge_pages_in_scope"], 0)
        self.assertFalse(report["errors"])
        self.assertFalse(report["warnings"])
        self.assertEqual(before, self.snapshot())

    def test_broken_link_has_source_location_and_failing_exit(self):
        self.write("wiki/INDEX.md", "# Index\n\n[Missing](missing.md)\n")
        status, report = self.check()
        self.assertEqual(status, 1)
        self.assertEqual(len(report["errors"]), 1)
        error = report["errors"][0]
        self.assertEqual((error["code"], error["file"], error["line"]),
                         ("missing_target", "wiki/INDEX.md", 3))
        self.assertEqual(error["target"], "missing.md")

    def test_unicode_formatting_duplicate_setext_and_html_anchors(self):
        self.write("wiki/guide.md", "# **用户** 画像\n# `api_name`\n"
                   "# 同名标题\n# 同名标题\nTitle\n-----\n<a id=\"custom\"></a>\n")
        index = "# Index\n" + "\n".join(
            "[Part](guide.md#" + fragment + ")"
            for fragment in ("用户-画像", "api_name", "同名标题-1", "title", "custom")
        ) + "\n"
        self.write("wiki/INDEX.md", index)
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["warnings"])
        self.write("wiki/INDEX.md", index + "[Wrong](guide.md#does-not-exist)\n")
        status, report = self.check()
        self.assertEqual(status, 1)
        self.assertEqual([issue["code"] for issue in report["errors"]], ["missing_anchor"])

    def test_images_spaces_parentheses_and_reference_links(self):
        self.write("wiki/guide(v1).md", "# Part\n")
        self.write("wiki/note with spaces.md", "# Note\n")
        self.write("raw/My Pic.png", b"test-image-target")
        self.write("wiki/INDEX.md", "# Index\n"
                   "[Guide](guide(v1).md \"Title\")\n"
                   "[Note](<note with spaces.md>)\n"
                   "[Reference][guide]\n[guide][]\n[guide]\n"
                   "![Photo](<../raw/My Pic.png>)\n"
                   "![Reference photo][image]\n"
                   "[guide]: guide(v1).md#part \"Reference title\"\n"
                   "[image]: <../raw/My Pic.png>\n")
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["warnings"])
        self.assertEqual(report["summary"]["local_links_checked"], 8)
        self.assertEqual(report["summary"]["knowledge_pages_reachable"], 2)

    def test_html_anchor_example_in_inline_code_is_not_a_real_anchor(self):
        self.write("wiki/guide.md", "# `api_name`\n`<a id=\"fake\"></a>`\n")
        self.write("wiki/INDEX.md", "# Index\n[Valid](guide.md#api_name)\n"
                   "[Not an anchor](guide.md#fake)\n")
        status, report = self.check()
        self.assertEqual(status, 1)
        self.assertEqual([(issue["code"], issue["target"]) for issue in report["errors"]],
                         [("missing_anchor", "guide.md#fake")])

    def test_examples_front_matter_and_comments_are_ignored(self):
        self.write("wiki/sample.md", "---\nexample: '[Yaml](missing-yaml.md)'\n---\n"
                   "# Sample\n`[Inline](missing-inline.md)`\n"
                   "``[Inline](missing-double.md)``\n"
                   "````markdown\n[Code](missing-code.md)\n```\n````\n"
                   "~~~text\n[Other](missing-tilde.md)\n~~~\n"
                   "<!-- [Comment](missing-comment.md) -->\n"
                   "[Real](missing-real.md)\n")
        self.write("wiki/INDEX.md", "# Index\n[Sample](sample.md)\n")
        status, report = self.check()
        self.assertEqual(status, 1)
        self.assertEqual([issue["target"] for issue in report["errors"]], ["missing-real.md"])
        self.assertEqual(report["errors"][0]["line"], 15)

    def test_navigation_follows_links_and_strict_fails_for_orphans(self):
        self.write("wiki/INDEX.md", "# Index\n[Topic](topic.md)\n")
        self.write("wiki/topic.md", "# Topic\n[Detail](detail.md)\n")
        self.write("wiki/detail.md", "# Detail\n")
        self.write("wiki/orphan.md", "# Orphan\n")
        status, report = self.check()
        self.assertEqual(status, 0)
        self.assertEqual(report["summary"]["knowledge_pages_reachable"], 2)
        self.assertEqual([(issue["code"], issue["file"]) for issue in report["warnings"]],
                         [("unreachable_page", "wiki/orphan.md")])
        status, _ = self.check("--strict")
        self.assertEqual(status, 1)

    def test_selected_scope_reads_anchor_target_without_following_its_links(self):
        self.write("README.md", "# Template\n[Broken](missing.md)\n")
        self.write("wiki/INDEX.md", "# Index\n[Topic](topic.md#topic)\n")
        self.write("wiki/topic.md", "# Topic\n[Broken](another-missing.md)\n")
        self.write("wiki/orphan.md", "# Orphan\n")
        status, report = self.check("--paths", "wiki/INDEX.md", "wiki/SELF.md")
        self.assertEqual(status, 0, report)
        self.assertEqual(report["scope"]["documents"], ["wiki/INDEX.md", "wiki/SELF.md"])
        self.assertEqual(report["scope"]["anchor_targets_read"], ["wiki/topic.md"])
        self.assertIn("global_reachability", [item["check"] for item in report["skipped_checks"]])
        self.assertNotIn("knowledge_pages_reachable", report["summary"])
        self.assertFalse(report["warnings"])

    def test_raw_source_links_are_only_checked_when_selected(self):
        self.write("raw/source.md", "# Original\n[Original relative link](src/build.md)\n")
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertNotIn("raw/source.md", report["scope"]["documents"])
        status, report = self.check("--paths", "raw/source.md")
        self.assertEqual(status, 1)
        self.assertEqual(report["errors"][0]["file"], "raw/source.md")

    def test_outside_root_is_not_read(self):
        (self.root.parent / "private.md").write_bytes(b"\xff")
        self.write("README.md", "# Template\n[Outside](../private.md#secret)\n")
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["errors"])
        self.assertEqual([issue["code"] for issue in report["warnings"]], ["outside_root"])
        self.assertFalse(report["scope"]["anchor_targets_read"])

    def test_invalid_root_or_selected_path_returns_two(self):
        for arguments in (("--root", str(self.root / "missing")),
                          ("--paths", "../private.md"),
                          ("--paths", str(self.root / "README.md")),
                          ("--paths", "missing.md")):
            with self.subTest(arguments=arguments):
                result = self.cli(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)

    def test_required_files_checked_even_in_selected_mode(self):
        (self.root / "wiki/SELF.md").unlink()
        status, report = self.check("--paths", "wiki/INDEX.md")
        self.assertEqual(status, 1)
        self.assertEqual([(issue["code"], issue["file"]) for issue in report["errors"]],
                         [("missing_required_file", "wiki/SELF.md")])

    def test_root_relative_links_use_repository_root(self):
        self.write("wiki/topic.md", "# Topic\n")
        self.write("wiki/INDEX.md", "# Index\n[Topic](/wiki/topic.md#topic)\n")
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["warnings"])
        self.assertEqual(report["summary"]["knowledge_pages_reachable"], 1)

    def test_external_urls_and_unsupported_syntax_are_explicit(self):
        self.write("raw/paper.pdf", b"test-pdf-target")
        self.write("README.md", "# Template\n[URL](https://example.com/never-fetch)\n"
                   "[Directory](wiki/)\n[[Missing Wiki Link]]\n"
                   "[PDF](raw/paper.pdf#page=2)\n")
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertEqual(report["summary"]["external_links_skipped"], 1)
        self.assertEqual({issue["code"] for issue in report["warnings"]},
                         {"directory_target", "unsupported_wikilink", "unchecked_fragment"})

    def test_unreadable_selected_document_is_reported(self):
        self.write("wiki/bad.md", b"\xff")
        status, report = self.check("--paths", "wiki/bad.md")
        self.assertEqual(status, 1)
        self.assertEqual([issue["code"] for issue in report["errors"]], ["unreadable_document"])
        self.assertEqual(report["summary"]["documents_checked"], 0)

    def test_symbolic_link_outside_root_is_not_read(self):
        outside = self.root.parent / "private.md"
        outside.write_bytes(b"\xff")
        try:
            (self.root / "wiki/external.md").symlink_to(outside)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(str(exc))
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["errors"])
        self.assertEqual([issue["code"] for issue in report["warnings"]], ["outside_root_document"])
        self.assertNotIn("wiki/external.md", report["scope"]["documents"])

    def test_symbolic_link_directory_is_reported_without_traversal(self):
        outside = self.root.parent / "external-directory"
        outside.mkdir()
        (outside / "private.md").write_bytes(b"\xff")
        try:
            (self.root / "wiki/external").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(str(exc))
        status, report = self.check()
        self.assertEqual(status, 0, report)
        self.assertFalse(report["errors"])
        self.assertEqual([issue["code"] for issue in report["warnings"]],
                         ["unchecked_symlink_directory"])
        self.assertEqual(report["scope"]["skipped_directories"], ["wiki/external"])


if __name__ == "__main__":
    unittest.main()
