#!/usr/bin/env python3
"""Read-only checks for the template's files, Markdown links and navigation.

Uses Python 3.9+ standard library. This is a deliberately limited Markdown
checker, not a renderer or an evidence/content validator.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED = (
    "README.md", "AGENTS.md", "raw/README.md", "wiki/README.md",
    "wiki/SELF.md", "wiki/INDEX.md",
)
MANAGEMENT = {"wiki/README.md", "wiki/SELF.md", "wiki/INDEX.md"}
IGNORED_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def mask(text: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in text)


def body_text(text: str) -> str:
    """Remove front matter, fenced examples and comments, preserving lines."""
    lines = text.splitlines(keepends=True)
    front = bool(lines and lines[0].strip() == "---")
    fence = None
    result = []
    for index, line in enumerate(lines):
        if front:
            result.append(mask(line))
            if index and line.strip() in {"---", "..."}:
                front = False
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            result.append(mask(line))
            if re.match(r"^ {0,3}" + re.escape(fence[0]) +
                        "{" + str(fence[1]) + r",}\s*$", line):
                fence = None
        elif opening:
            fence = (opening[1][0], len(opening[1]))
            result.append(mask(line))
        else:
            result.append(line)
    return re.sub(r"<!--[\s\S]*?(?:-->|$)", lambda match: mask(match[0]),
                  "".join(result))


def without_inline_code(text: str) -> str:
    pattern = re.compile(r"(?<![\\`])(`+)(?!`)")
    cursor = 0
    parts = []
    while True:
        start = pattern.search(text, cursor)
        if not start:
            parts.append(text[cursor:])
            break
        end = re.search(r"(?<!`)" + re.escape(start[1]) + r"(?!`)",
                        text[start.end():])
        if not end:
            parts.append(text[cursor:start.end()])
            cursor = start.end()
            continue
        stop = start.end() + end.end()
        parts.extend((text[cursor:start.start()], mask(text[start.start():stop])))
        cursor = stop
    return "".join(parts)


def slug(title: str) -> str:
    title = re.sub(r"!?\[([^\]]*)\]\([^\n]*?\)", r"\1", title)
    title = re.sub(r"<[^>]*>", "", title)
    title = re.sub(r"(?<!`)(`+)(?!`)(.*?)\1", r"\2", title)
    for pattern in (r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1",
                    r"(?<!\w)(\*|_)(?=\S)(.+?)(?<=\S)\1(?!\w)",
                    r"(~~)(?=\S)(.+?)(?<=\S)\1"):
        title = re.sub(pattern, r"\2", title)
    title = re.sub(r"\\([\\`*{}\[\]()#+\-.!_>~])", r"\1", title)
    title = html.unescape(title).lower().replace(" ", "-")
    return "".join(char for char in title if char in "-_" or
                   (not char.isspace() and
                    unicodedata.category(char)[0] not in "PS"))


def anchors(body: str) -> set[str]:
    found = set()
    lines = body.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^ {0,3}#{1,6}(?:\s+|$)(.*)$", line)
        title = None
        if heading:
            title = re.sub(r"\s+#+\s*$", "", heading[1]).strip()
        elif (index and re.match(r"^ {0,3}(?:=+|-+)\s*$", line) and
              lines[index - 1].strip() and
              not re.match(r"^\s*(?:[-*+] |\d+[.)] |>)", lines[index - 1])):
            title = lines[index - 1].strip()
        if title is not None:
            base = slug(title)
            candidate, number = base, 0
            while candidate in found:
                number += 1
                candidate = base + "-" + str(number)
            found.add(candidate)
    for match in re.finditer(r"<[A-Za-z][^>]*?\s(?:id|name)\s*=\s*"
                             r"(?:\"([^\"]+)\"|'([^']+)'|([^\s>]+))",
                             without_inline_code(body)):
        found.add(html.unescape(next(value for value in match.groups() if value)))
    return found


def unescape(value: str) -> str:
    return html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])",
                               r"\1", value))


def destination(text: str, start: int) -> tuple[str, int] | None:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor == len(text):
        return None
    first = cursor
    if text[cursor] == "<":
        cursor += 1
        first = cursor
        while cursor < len(text):
            if text[cursor] == "\\":
                cursor += 2
                continue
            if text[cursor] == ">":
                return unescape(text[first:cursor]), cursor + 1
            if text[cursor] == "\n":
                return None
            cursor += 1
        return None
    depth = 0
    while cursor < len(text):
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text):
            cursor += 2
            continue
        if char.isspace() or (char == ")" and depth == 0):
            break
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        cursor += 1
    if depth:
        return None
    return unescape(text[first:cursor]), cursor


def closing_link(text: str, cursor: int) -> int | None:
    before = cursor
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    if cursor < len(text) and text[cursor] == ")":
        return cursor + 1
    if cursor == before or cursor == len(text) or text[cursor] not in "\"'(":
        return None
    closer = ")" if text[cursor] == "(" else text[cursor]
    cursor += 1
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
        elif text[cursor] == closer:
            cursor += 1
            while cursor < len(text) and text[cursor].isspace():
                cursor += 1
            return cursor + 1 if cursor < len(text) and text[cursor] == ")" else None
        else:
            cursor += 1
    return None


def bracket(text: str, start: int) -> tuple[str, int] | None:
    depth, cursor = 1, start + 1
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] == "[":
            depth += 1
        elif text[cursor] == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1:cursor], cursor + 1
        cursor += 1
    return None


def reference_id(label: str) -> str:
    return " ".join(unescape(label).split()).casefold()


@dataclass(frozen=True)
class Link:
    target: str
    line: int


def links(body: str) -> tuple[list[Link], list[Link]]:
    text = without_inline_code(body)
    unsupported = []
    for match in re.finditer(r"\[\[[^\]\n]+\]\]", text):
        unsupported.append(Link(match[0], text.count("\n", 0, match.start()) + 1))
    text = re.sub(r"\[\[[^\]\n]+\]\]", lambda match: mask(match[0]), text)
    definitions = {}
    for match in re.finditer(r"^ {0,3}\[([^\]\n]+)\]:[ \t]*(.*)$", text, re.M):
        parsed = destination(match[2], 0)
        if parsed and not match[1].startswith("^"):
            definitions.setdefault(reference_id(match[1]), parsed[0])
    text = re.sub(r"^ {0,3}\[[^\]\n]+\]:[^\n]*", lambda match: mask(match[0]),
                  text, flags=re.M)
    result, cursor = [], 0
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] != "[":
            cursor += 1
            continue
        label = bracket(text, cursor)
        if not label:
            cursor += 1
            continue
        value, end = label
        target, stop = None, end
        if end < len(text) and text[end] == "(":
            parsed = destination(text, end + 1)
            if parsed:
                close = closing_link(text, parsed[1])
                if close:
                    target, stop = parsed[0], close
        elif end < len(text) and text[end] == "[":
            ref = bracket(text, end)
            if ref:
                target = definitions.get(reference_id(ref[0] or value))
                stop = ref[1]
        else:
            target = definitions.get(reference_id(value))
        if target is not None:
            result.append(Link(target, text.count("\n", 0, cursor) + 1))
        cursor = stop
    return result, unsupported


def markdown_files(folder: Path, excluded: list[Path]) -> list[Path]:
    result = []
    if folder.is_symlink():
        excluded.append(folder)
        return result
    for base, directories, files in os.walk(folder, followlinks=False):
        symlinks = {name for name in directories if (Path(base) / name).is_symlink()}
        excluded.extend(Path(base) / name for name in sorted(symlinks))
        directories[:] = sorted(name for name in directories
                                if name not in IGNORED_DIRS and name not in symlinks)
        result.extend(Path(base) / name for name in sorted(files)
                      if Path(name).suffix.lower() == ".md")
    return result


class Checker:
    def __init__(self, root: Path, documents: list[Path], requested: list[str] | None,
                 excluded: list[Path]):
        self.root, self.documents, self.requested = root, documents, requested
        self.excluded = sorted(set(excluded))
        self.errors, self.warnings = [], []
        self.cache = {}
        self.graph = {}
        self.local_links = self.external_links = 0
        self.skipped = [
            {"check": "content_and_evidence", "reason": "事实、引用支持、解释深度与真实运行需人工 review。"},
            {"check": "external_urls", "reason": "外部 URL 只识别，不联网核验。"},
            {"check": "full_markdown_rendering", "reason": "支持常用链接和标题；复杂 Markdown、HTML、缩进代码及渲染器差异需人工核对。"},
        ]
        if requested is None:
            self.skipped.append({"check": "raw_source_bodies", "reason": "默认保留原始来源环境，只扫描 raw/README.md。"})
        else:
            self.skipped.append({"check": "global_reachability", "reason": "局部检查不推断全库 INDEX 可达性。"})

    def relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def issue(self, level: str, code: str, path: Path, line: int, message: str,
              target: str | None = None) -> None:
        item = {"code": code, "file": self.relative(path), "line": line, "message": message}
        if target is not None:
            item["target"] = target
        (self.errors if level == "error" else self.warnings).append(item)

    def read(self, path: Path):
        if path not in self.cache:
            try:
                body = body_text(path.read_text(encoding="utf-8-sig"))
                self.cache[path] = (anchors(body), *links(body))
            except (OSError, UnicodeError) as exc:
                self.cache[path] = None
                self.issue("error", "unreadable_document", path, 1,
                           "文档无法按 UTF-8 读取：" + str(exc))
        return self.cache[path]

    def check_link(self, document: Path, link: Link) -> None:
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link.target) or link.target.startswith("//"):
            self.external_links += 1
            return
        self.local_links += 1
        try:
            parsed = urlsplit(link.target)
            part, fragment = unquote(parsed.path), unquote(parsed.fragment)
            target = ((self.root / part.lstrip("/")) if part.startswith("/") else
                      (document.parent / part if part else document)).resolve()
        except (ValueError, OSError, RuntimeError) as exc:
            self.issue("error", "invalid_local_link", document, link.line,
                       "本地目标无法解析：" + str(exc), link.target)
            return
        if not inside(target, self.root):
            self.issue("warning", "outside_root", document, link.line,
                       "目标越出 Wiki 根目录，未读取或验证。", link.target)
            return
        if not target.exists():
            self.issue("error", "missing_target", document, link.line,
                       "本地链接或图片的目标不存在。", link.target)
            return
        if target.is_dir():
            self.issue("warning", "directory_target", document, link.line,
                       "链接指向目录，需人工核对实际阅读入口。", link.target)
            return
        if not target.is_file():
            self.issue("warning", "special_file_target", document, link.line,
                       "目标不是普通文件，未读取。", link.target)
            return
        self.graph.setdefault(document, set()).add(target)
        if fragment:
            if target.suffix.lower() != ".md":
                self.issue("warning", "unchecked_fragment", document, link.line,
                           "非 Markdown 文件的片段未核验。", link.target)
            else:
                content = self.read(target)
                if content is not None and fragment not in content[0]:
                    self.issue("error", "missing_anchor", document, link.line,
                               "目标文档中未找到对应标题或简单 HTML 锚点。", link.target)

    def run(self) -> dict:
        for folder in self.excluded:
            self.issue("warning", "unchecked_symlink_directory", folder, 1,
                       "符号链接目录未遍历，需核对实际入口或明确指定其中的文件。")
        for name in REQUIRED:
            if not (self.root / name).is_file():
                self.issue("error", "missing_required_file", self.root / name, 1,
                           "模板管理文件缺失或不是普通文件。")
        scanned = []
        for original in self.documents:
            document = original.resolve()
            if not inside(document, self.root):
                self.issue("warning", "outside_root_document", original, 1,
                           "文档通过符号链接越出根目录，未读取。")
                continue
            if document in scanned:
                continue
            scanned.append(document)
            content = self.read(document)
            if content is None:
                continue
            for unsupported in content[2]:
                self.issue("warning", "unsupported_wikilink", document, unsupported.line,
                           "非标准双链未检查目标或导航。", unsupported.target)
            for link in content[1]:
                self.check_link(document, link)
        wiki_documents = {path for path in scanned if
                          inside(path, self.root / "wiki")}
        knowledge = {path for path in wiki_documents if self.relative(path) not in MANAGEMENT}
        summary = {"documents_checked": sum(self.cache.get(path) is not None for path in scanned),
                   "local_links_checked": self.local_links,
                   "external_links_skipped": self.external_links,
                   "knowledge_pages_in_scope": len(knowledge)}
        if self.requested is None:
            entry = self.root / "wiki/INDEX.md"
            if entry not in self.cache or self.cache[entry] is None:
                self.skipped.append({"check": "global_reachability", "reason": "INDEX 缺失或无法读取，可达性未判断。"})
            else:
                reached, queue = set(), [entry]
                while queue:
                    current = queue.pop()
                    if current in reached:
                        continue
                    reached.add(current)
                    queue.extend((self.graph.get(current, set()) & wiki_documents) - reached)
                summary["knowledge_pages_reachable"] = len(knowledge & reached)
                for page in sorted(knowledge - reached):
                    self.issue("warning", "unreachable_page", page, 1,
                               "无法从 wiki/INDEX.md 沿 Wiki 链接到达此知识页面。")
        for items in (self.errors, self.warnings):
            items.sort(key=lambda item: (item["file"], item["line"], item["code"], item.get("target", "")))
        summary.update(errors=len(self.errors), warnings=len(self.warnings))
        return {
            "root": str(self.root),
            "scope": {"mode": "full" if self.requested is None else "selected",
                      "requested_paths": self.requested,
                      "documents": [self.relative(path) for path in sorted(scanned)],
                      "anchor_targets_read": [self.relative(path) for path in sorted(set(self.cache) - set(scanned))],
                      "skipped_directories": [self.relative(path) for path in self.excluded],
                      "required_files": list(REQUIRED)},
            "summary": summary, "errors": self.errors, "warnings": self.warnings,
            "skipped_checks": self.skipped,
            "verification": "只读机械检查；不能证明事实、来源支持、知识质量或真实运行。",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Wiki root directory (default: current directory)")
    parser.add_argument("--paths", nargs="+", help="Selected Markdown files/directories, relative to root")
    parser.add_argument("--strict", action="store_true", help="Return 1 for warnings as well as errors")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error("--root must be an existing directory")
    documents, excluded = [], []
    if args.paths is None:
        documents.extend(path for path in root.iterdir() if path.suffix.lower() == ".md" and path.is_file())
        for name in ("wiki", ".agents/skills"):
            documents.extend(markdown_files(root / name, excluded))
        if (root / "raw/README.md").is_file():
            documents.append(root / "raw/README.md")
    else:
        for name in args.paths:
            path = root / name
            if Path(name).is_absolute() or not inside(path.resolve(), root):
                parser.error("--paths must be relative paths inside --root: " + name)
            if path.is_dir():
                documents.extend(markdown_files(path, excluded))
            elif path.is_file() and path.suffix.lower() == ".md":
                documents.append(path)
            else:
                parser.error("--paths target must be an existing Markdown file or directory: " + name)
    result = Checker(root, sorted(set(documents)), args.paths, excluded).run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["errors"] or (args.strict and result["warnings"])))


if __name__ == "__main__":
    raise SystemExit(main())
