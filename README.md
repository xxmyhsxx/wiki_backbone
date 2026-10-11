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

常用操作包括：

| 操作 | 何时使用 | 工作结果 |
| --- | --- | --- |
| **Ingest：资料入库** | 有新来源需要整理时。 | 创建或修订知识页面，同步来源引用、页面链接和导航。 |
| **Query：查询与探索** | 需要解释、比较或分析问题时。 | 利用已有页面及来源回答问题；值得保留的分析可以写回 Wiki。 |
| **Lint：检查与维护** | 检查 Wiki 的内容与组织时。 | 发现矛盾、过时内容、缺失链接和知识空白，明确需要回查或修订的内容。 |

入库增加和更新知识，查询推动进一步探索，维护帮助页面保持可用。这些名称表示 Agent 的任务类型，具体流程可以按 Wiki 的用途确定。用户负责选择来源、判断重点和复核重要结论，Agent 按约定整理与维护。

## 项目使用

### 模板提供什么

模板包含项目说明、Agent 工作约定、来源规则、知识页面规范、Wiki 定位与现状说明，以及导航。`wiki-init` 结合用户需求定制这些文件，建立适合用户的用途说明、组织方式和使用入口。

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
        │   └── README.md      预留设计入口
        ├── wiki-query/
        │   └── README.md      预留设计入口
        └── wiki-review/
            └── README.md      预留设计入口
```

模板使用本地 Markdown 文件保存内容，以相对链接建立导航，通过 Git 提交记录版本。`raw/` 保存来源，`wiki/` 组织知识；具体分类根据用户需求和实际内容建立。

项目中的 Skill 按以下状态维护：

| Skill | 用途 | 当前状态与入口 |
| --- | --- | --- |
| `skill-creator` | 创建与修改 Skill。 | 已迁入；[设计规范](.agents/skills/skill-creator/README.md)、[执行规范](.agents/skills/skill-creator/SKILL.md)。 |
| `wiki-init` | 定制用户自己的 Wiki。 | [设计](.agents/skills/wiki-init/README.md)与[执行规范](.agents/skills/wiki-init/SKILL.md)已同步。 |
| `wiki-ingest` | 将来源中的知识增量整合到 Wiki。 | [预留设计入口](.agents/skills/wiki-ingest/README.md)，尚未实现。 |
| `wiki-query` | 查找知识并开展查询。 | [预留设计入口](.agents/skills/wiki-query/README.md)，尚未实现。 |
| `wiki-review` | 审核知识、证据与组织质量。 | [预留设计入口](.agents/skills/wiki-review/README.md)，尚未实现。 |

创建或修改 Skill 时使用本项目的 `skill-creator`：README 保存设计，SKILL.md 保存执行规范。预留入口用于后续讨论，完成设计与实现后再作为可调用 Skill 使用。初始化后的资料入库、查询与维护，也可以让 Agent 按 Wiki 的工作约定执行。

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
