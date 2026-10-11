# LLM Wiki 通用模板

本项目提供通用 LLM Wiki 模板，并通过 `wiki-init` Skill 帮助用户完成初始化。你可以在模板基础上确定用途、知识范围和组织方式，建立自己的 Wiki。

## LLM Wiki 介绍

### 是什么

LLM Wiki 是一种用大语言模型（LLM）持续构建和维护知识库的方式。用户提供资料和方向，LLM 将资料整理为相互链接的知识页面，并随着新的资料和讨论补充、修订内容。阅读与分析的成果由此保留下来，供之后复用。这个思路参考 [Karpathy 的 LLM Wiki 原始说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

### 核心特点

- **知识持续积累。** 概念解释、方法和分析成为可反复使用的页面。
- **多份来源相互整合。** 围绕主题综合资料，保留各自的依据与差异。
- **页面之间建立关联。** 通过链接连接概念、方法与比较，便于继续阅读和探索。
- **已有知识持续修订。** 新资料可以补充解释、改变结论，或揭示需要核对的矛盾。

### 如何运作

运行时，Agent 根据工作约定查阅来源和已有页面，执行整理、查询或维护任务。三个部分各有职责：

- **来源资料**保存可回查的原文及忠实副本，为解释和结论提供依据。
- **知识页面**保存经过理解和组织的内容，以及页面之间的联系。
- **工作约定**说明内容如何组织、来源如何引用，以及任务如何完成。

常用操作包括以下几类。原始说明中的 Lint 包含内容与组织检查；本模板通过 Review 和 Lint 分别完成内容核验与机械检查。[参考原始说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

| 操作 | 何时使用 | 工作结果 |
| --- | --- | --- |
| **Ingest：资料入库** | 有新来源需要整理时。 | 创建或修订知识页面，同步来源引用、页面链接和导航。 |
| **Query：查询与探索** | 需要定位、解释、比较或分析问题时。 | 利用实际页面及来源回答问题；用户要求保存时写回有价值的分析。 |
| **Review：内容审核** | 评估知识、证据与解释质量时。 | 回查关键主张，检查解释断点、条件差异、矛盾与重要知识缺口，提出有依据的建议。 |
| **Lint：机械检查** | 检查文件、链接与导航时。 | 用只读工具发现管理文件缺失、断链、失效锚点和无法从 INDEX 到达的知识页。 |

入库增加和更新知识，查询推动进一步探索，维护帮助页面保持可用。这些名称表示 Agent 的任务类型，具体流程可以按 Wiki 的用途确定。用户负责选择来源、判断重点和复核重要结论，Agent 按约定整理与维护。

## 项目使用

### 模板提供什么

模板包含项目说明、Agent 工作约定、来源规则、知识页面规范、Wiki 定位与现状说明，以及导航。`wiki-init` 结合用户需求定制这些文件；初始化后通过 ingest、query、review 和 lint 持续积累、使用与维护知识。

```text
.
├── README.md                  项目介绍与使用入口
├── AGENTS.md                  Agent 工作约定
├── .gitignore                 本地文件忽略规则
├── raw/
│   └── README.md              来源资料的保存规则
├── wiki/
│   ├── README.md              知识页面规范
│   ├── SELF.md                Wiki 定位、范围与当前画像
│   └── INDEX.md               知识导航
└── .agents/
    └── skills/
        ├── skill-creator/
        │   ├── README.md      Skill 设计与维护规范
        │   └── SKILL.md       Skill 创建与修改方法
        ├── wiki-init/
        │   ├── README.md      初始化设计
        │   └── SKILL.md       初始化执行规范
        ├── wiki-ingest/
        │   ├── README.md      资料入库设计
        │   └── SKILL.md       资料入库执行规范
        ├── wiki-query/
        │   ├── README.md      查询与探索设计
        │   └── SKILL.md       查询与写回执行规范
        ├── wiki-review/
        │   ├── README.md      内容审核设计
        │   └── SKILL.md       审核与修复执行规范
        └── wiki-lint/
            ├── README.md     机械检查设计
            ├── SKILL.md      检查与修复执行规范
            ├── scripts/
            │   └── check_wiki.py
            └── tests/
                └── test_check_wiki.py
```

模板使用本地 Markdown 文件保存内容，以相对链接建立导航，通过 Git 提交记录版本。`raw/` 保存来源，`wiki/` 组织知识；具体分类根据用户需求和实际内容建立。

项目中的 Skill 按以下状态维护：

| Skill | 用途 | 当前状态与入口 |
| --- | --- | --- |
| `skill-creator` | 创建与修改 Skill。 | 已迁入；[设计规范](.agents/skills/skill-creator/README.md)、[执行规范](.agents/skills/skill-creator/SKILL.md)。 |
| `wiki-init` | 定制用户自己的 Wiki。 | [设计](.agents/skills/wiki-init/README.md)与[执行规范](.agents/skills/wiki-init/SKILL.md)已同步。 |
| `wiki-ingest` | 将来源中的知识增量整合到 Wiki。 | [设计](.agents/skills/wiki-ingest/README.md)、[执行规范](.agents/skills/wiki-ingest/SKILL.md)。 |
| `wiki-query` | 定位、解释、比较与分析，按要求写回。 | [设计](.agents/skills/wiki-query/README.md)、[执行规范](.agents/skills/wiki-query/SKILL.md)。 |
| `wiki-review` | 审核证据、解释深度、关联与知识缺口。 | [设计](.agents/skills/wiki-review/README.md)、[执行规范](.agents/skills/wiki-review/SKILL.md)。 |
| `wiki-lint` | 检查文件、链接、锚点与导航可达性。 | [设计](.agents/skills/wiki-lint/README.md)、[执行规范](.agents/skills/wiki-lint/SKILL.md)、[检查工具](.agents/skills/wiki-lint/scripts/check_wiki.py)。 |

创建或修改 Skill 时使用本项目的 `skill-creator`：README 保存设计，SKILL.md 保存执行规范。每个 Wiki Skill 都有完成条件，评估用途、证据、实际产物及核验边界；具体指标见相应文件。

### 如何初始化

1. **获取模板。** 当前模板以本地 Git 仓库提供。将下面的 `/path/to/wiki_backbone` 替换为模板仓库的实际路径，在新副本中开始使用：

   ```bash
   git clone /path/to/wiki_backbone my-wiki
   cd my-wiki
   ```

   模板发布到远程仓库后，可将本地路径替换为远程仓库地址。

2. **使用 `wiki-init`。** 在自己的模板副本中打开 Agent，说明用途、主题和已有资料。可以这样开始：

   ```text
   请使用 .agents/skills/wiki-init/SKILL.md 初始化当前 Wiki。
   我希望用它整理……，主要用于……。
   我已有的资料是……。
   请先和我讨论定位、范围和目录安排，再完成已确定的方案。
   ```

   如需初始化到其他目录，同时提供目标位置。

3. **确定方案并完成初始化。** 与 Agent 明确用途、范围和组织方式。Agent 根据方案定制说明与工作约定，填写 `wiki/SELF.md`，调整必要目录和导航，并检查链接与描述是否一致。

没有初始资料时，也可以先完成结构与约定的初始化；SELF 如实记录当前内容和下一步。完成后，查看 README、SELF 和 INDEX，确认用途、组织方式和使用入口符合你的需求。

### 初始化后如何开始

初始化后，README 介绍用户自己的 Wiki，SELF 记录定位、范围、实际已有内容和下一步。根据当前任务选择入口：

- 查看定位和当前状态：[wiki/SELF.md](wiki/SELF.md)。
- 浏览知识：[wiki/INDEX.md](wiki/INDEX.md)。
- 保存来源资料：[raw/README.md](raw/README.md)。
- 编写与维护知识页面：[wiki/README.md](wiki/README.md)。
- 了解 Agent 的工作约定：[AGENTS.md](AGENTS.md)。

可以直接向 Agent 描述任务，也可以明确指定 Skill：

| 任务 | 请求示例 |
| --- | --- |
| 资料入库 | 使用 wiki-ingest 读取这份资料，检查已有覆盖，再将有依据的增量写入 Wiki。 |
| 查询与探索 | 使用 wiki-query 比较这两种方法，引用已有页面，说明可比条件和证据缺口。 |
| 内容审核 | 使用 wiki-review 审核这些页面的关键主张、解释深度和关联，给出依据及修改建议。 |
| 机械检查 | 使用 wiki-lint 检查当前 Wiki 的文件、链接、锚点和导航。 |

只要求查询或审核时，Agent 交付结果与建议；要求保存或修复时，按明确范围完成改动和复查。

lint 工具依赖 Python 3.9+ 标准库，可从项目根目录直接运行：

```bash
python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root .
python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root . --paths wiki/SELF.md wiki/INDEX.md
```

检查输出 JSON，列出实际范围、错误、提醒和跳过项；加 `--strict` 可让提醒也返回失败。局部检查跳过全库导航可达性。在 raw/ 中默认只检查 raw/README.md，原始资料正文在明确指定时检查，避免误判原文中的相对链接。支持范围见 [wiki-lint 设计](.agents/skills/wiki-lint/README.md#51-工具检查范围)。机械检查通过后，事实、引用支持与知识解释仍需依据来源核验。

### 设计参考

- [Karpathy 的 LLM Wiki 原始说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：来源整合、持久知识页面、带依据的查询和持续维护。
- [wpzero/karpathy-llm-wiki](https://github.com/wpzero/karpathy-llm-wiki)：将 ingest、query 和 lint 整理为 Agent 工作流程的实现参考。
- [godstale/LLM-WiKi](https://github.com/godstale/LLM-WiKi)：将结构检查工具与 Agent 内容检查配合使用的实现参考。

本模板结合这些思路和自身约定设计流程：raw 保留来源，wiki 组织可独立阅读的知识，通过标准 Markdown 链接与 INDEX 建立阅读路径，用 Git 记录修改。具体分类、来源格式和解释深度在初始化时确定。
