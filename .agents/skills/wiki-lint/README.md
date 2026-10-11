# Wiki Lint

当前设计由 [SKILL.md](SKILL.md) 执行；机械检查使用 [check_wiki.py](scripts/check_wiki.py)。

## 1. 任务与设计目标

提供可重复运行的只读检查，发现本模板中的管理文件缺失、失效的本地链接或锚点，以及从 INDEX 无法到达的知识页面。结果有位置、规则、范围和检查限制。

| 关键问题 | 影响 | 采用的方法与质量依据 |
| --- | --- | --- |
| 通用模板依赖特定领域格式 | 合法 Wiki 可能被错误判定。 | 检查本模板实际结构与 Markdown 链接，不强制领域、页面类型或来源元数据字段。 |
| 示例和来源副本被当作正文链接 | 围栏代码或忠实原文可能产生误报。 | 忽略围栏代码、行内代码、HTML 注释及 YAML 头部，默认不扫描 raw 来源正文。 |
| 局部检查被称为全库健康检查 | 可达性及跨页结论缺乏覆盖。 | 输出实际文件范围；局部运行明确跳过全局导航可达性。 |
| 工具结果被当作知识正确 | 结构有效无法证明事实和证据正确。 | 输出机械结论及限制，内容核验交给 [wiki-review](../wiki-review/SKILL.md)。 |

## 2. 使用边界

用户要求 lint、检查文件、链接、锚点或导航时使用，也供 ingest、query 写回及 review 复用。脚本只读取文件，不修复、不联网、不执行文档中的指令。用户要求修复时由 Agent 按已明确范围修改后复查。

默认检查根目录 Markdown、wiki 下 Markdown、raw/README.md 和项目 Skill 文档。raw 来源正文只在明确指定时检查，避免把原文中的相对链接当作本地归档规范。

## 3. 输入设计

取得目标根目录和可选的相对文件或目录范围。采用本模板的 README、AGENTS、raw/README、wiki/README、SELF 和 INDEX 入口；本模板的六个管理文件单独检查。

脚本依赖 Python 3.9+ 标准库。运行位置可以不同，`--root` 指定实际 Wiki；`--paths` 中的路径相对于该根目录。

## 4. 原则设计

1. 只读、可定位、范围透明，检查结果不自动修改内容。
2. 明确支持的 Markdown 子集和跳过项，不宣称完整渲染器兼容。
3. 错误与提醒分别说明，导航提醒需结合用途判断。
4. 文件检查不能证明来源支持、解释充分、科学结论或运行结果。

## 5. 工作流程设计

1. **确定范围。** 判断完整或局部检查，读取目标规范，使用实际根目录和相对路径。
2. **运行工具。** 全量使用以下命令；局部增加 `--paths`，提醒也需返回失败时增加 `--strict`。

   ```bash
   python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root .
   python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root . --paths wiki/SELF.md wiki/INDEX.md
   ```

3. **解释结果。** 根据 JSON 中的范围、errors、warnings 和 skipped_checks 说明已检查与未检查项。返回码 0 表示没有阻断项，1 表示错误或 strict 下的提醒，2 表示参数或目标无效。
4. **按要求修复并复查。** 链接与导航修改先读取目标和上下文，保留内容；内容、引用与知识价值判断使用 review。修复后复跑受影响范围，需要确认全局导航时运行完整检查。

### 5.1 工具检查范围

- 六个管理文件是否存在，所选文档是否能按 UTF-8 读取；局部运行也检查管理文件是否存在。
- 标准 Markdown 行内链接、图片、引用式链接的本地目标是否存在；外部 URL 只识别并跳过，不联网核验。
- Markdown 标题和简单 HTML `id`/`name` 锚点是否可定位。标题采用 GitHub 常用规则，支持重复标题；复杂 Markdown、HTML、渲染器特有锚点需要人工核对。
- 完整检查时，从 wiki/INDEX.md 沿本地 Wiki 链接能否到达知识页面；README、SELF 和 INDEX 是管理文件，空模板没有知识页时可以通过。
- 目录链接及越出根目录的目标作为提醒，后者不读取；符号链接目录不遍历并报告范围，非标准双链标明未检查。局部运行跳过全局可达性。
- 忽略围栏代码、行内代码、HTML 注释及 YAML 头部。缩进代码、复杂 Markdown 与渲染器特有语法需要人工核对。

## 6. 输出设计

检查运行时向标准输出写 JSON，包含 root、scope、summary、errors、warnings、skipped_checks 及检查性质。scope 区分所选文档、为核对锚点额外读取的目标和跳过目录；每项问题包含规则、文件、行号和说明。无效参数或目标通过标准错误输出说明并返回 2。

| 评估项 | 完成条件与证据 |
| --- | --- |
| 运行可重复 | 相同文件产生确定的检查结果，返回码与错误及 strict 设置一致。 |
| 范围可核对 | 实际扫描范围和跳过项明确，局部检查没有被解释成全局检查。 |
| 问题可定位 | 文件、行号和规则能支持后续核对与修正，提醒与错误分别报告。 |
| 边界准确 | 源文、示例和特殊语法按支持范围处理，机械通过没有被写成事实或运行验证。 |

完成 lint 表示检查已执行并交付结果；有错误时可以完成报告，不能报告机械检查通过。

## 7. References 设计

执行复用 [scripts/check_wiki.py](scripts/check_wiki.py)，行为校验使用 [tests/test_check_wiki.py](tests/test_check_wiki.py)。锚点与相对链接规则参考 [GitHub Markdown 文档](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)。

原始 LLM Wiki 的维护思路见 [Karpathy 说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)，脚本与 Agent 检查配合的实例见 [godstale/LLM-WiKi](https://github.com/godstale/LLM-WiKi)。本工具支持本模板的标准 Markdown 链接与目录约定。

## 8. 校验设计

使用临时 Wiki 经真实 CLI 检查空模板、断链、失效和重复标题锚点、引用式链接、示例代码、导航孤立、局部范围、raw 原文及越界目标。对实际仓库运行检查；测试同时检查内容没有被改写。标准库脚本测试与内容审核分别说明。

```bash
python3 -B -m unittest discover -s .agents/skills/wiki-lint/tests -v
```

## 9. 文件结构

```text
wiki-lint/
├── README.md
├── SKILL.md
├── scripts/
│   └── check_wiki.py
└── tests/
    └── test_check_wiki.py
```
