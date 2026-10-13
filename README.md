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

常用操作包括以下几类。Lint 组织一次 Wiki 检查：用工具核对结构，查看 raw 基础情况，并复用 Review 核验知识内容；Review 也可单独用于指定内容的深入审核。[参考原始说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

| 操作 | 何时使用 | 工作结果 |
| --- | --- | --- |
| **Ingest：资料入库** | 有新来源需要整理时。 | 创建或修订知识页面，同步来源引用、页面链接和导航。 |
| **Query：查询与探索** | Wiki 内外的项目需要定位、解释、比较或分析知识时。 | 只读知识页面给出带依据的结果，新增独立查询反馈日志。 |
| **Review：内容审核** | 评估知识、证据与解释质量时。 | 回查关键主张，检查解释断点、条件差异、矛盾与重要知识缺口，提出有依据的建议。 |
| **Lint：Wiki 检查** | 检查整个 Wiki 或本次改动时。 | raw 做基础检查；工具核对结构，AI 检查 Wiki 内容、引用、导航、组织、一致性与当前状态。 |

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
        │   ├── README.md      查询导航与反馈设计
        │   └── SKILL.md       查询导航与反馈执行规范
        ├── wiki-review/
        │   ├── README.md      内容审核设计
        │   └── SKILL.md       审核与修复执行规范
        └── wiki-lint/
            ├── README.md     Wiki 检查设计
            ├── SKILL.md      检查与修复执行规范
            ├── scripts/
            │   └── check_wiki.py
            └── tests/
                └── test_check_wiki.py
```

模板使用本地 Markdown 文件保存内容，以相对链接建立导航，通过 Git 提交记录版本。`raw/` 保存来源，`wiki/` 组织知识；具体分类根据用户需求和实际内容建立。

想先看实际产物，可以阅读 [完整示例](examples/llm-wiki-demo/README.md)：两份固定版本来源如何形成知识页面，新资料补充了什么，以及重复入库、查询与审核怎样验证。示例位于独立目录，供理解和参考；自己的 Wiki 仍按用途初始化。

项目中的 Skill 按以下状态维护：

| Skill | 用途 | 当前状态与入口 |
| --- | --- | --- |
| `skill-creator` | 创建与修改 Skill。 | 已迁入；[设计规范](.agents/skills/skill-creator/README.md)、[执行规范](.agents/skills/skill-creator/SKILL.md)。 |
| `wiki-init` | 定制用户自己的 Wiki。 | [设计](.agents/skills/wiki-init/README.md)与[执行规范](.agents/skills/wiki-init/SKILL.md)已同步。 |
| `wiki-ingest` | 将来源中的知识增量整合到 Wiki。 | [设计](.agents/skills/wiki-ingest/README.md)、[执行规范](.agents/skills/wiki-ingest/SKILL.md)。 |
| `wiki-query` | 为 Wiki 内外的模型提供知识导航与查询，回传独立反馈。 | [设计](.agents/skills/wiki-query/README.md)、[执行规范](.agents/skills/wiki-query/SKILL.md)；初始化定制为 `query-<wiki-id>` 并安装同名镜像。 |
| `wiki-review` | 审核证据、解释深度、关联与知识缺口。 | [设计](.agents/skills/wiki-review/README.md)、[执行规范](.agents/skills/wiki-review/SKILL.md)。 |
| `wiki-lint` | 组织 raw 基础检查、工具结构检查与 Wiki 内容核验。 | [设计](.agents/skills/wiki-lint/README.md)、[执行规范](.agents/skills/wiki-lint/SKILL.md)、[结构工具](.agents/skills/wiki-lint/scripts/check_wiki.py)。 |

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

3. **逐项确定方案并完成初始化。** 先与 Agent 确定用途和内容边界，再确认可能的资料来源及原件、转录的保存形式。raw 按入库日期保存，每条包含原件、转录文章和说明。Agent 检索相关材料，推荐 Wiki 目录、候选页面及其关系，再根据已确认的 raw、Wiki 规范推荐检查项。方案确定后定制说明与工作约定，填写 `wiki/SELF.md`，将实际页面加入导航并核对。

   同时确定查询 Skill 名称、Wiki 的绝对位置和镜像安装目录，生成自包含的 `query-<wiki-id>`，创建 `query-feedback/` 并安装同名、同内容的镜像。最后从 Wiki 外的工作目录验证查询与反馈回传。

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
| 查询与探索 | 使用初始化定制的 query Skill 比较这两种方法，引用 Wiki 页面，说明可比条件与知识缺口，回传查询反馈。 |
| 内容审核 | 使用 wiki-review 审核这些页面的关键主张、解释深度和关联，给出依据及修改建议。 |
| Wiki 检查 | 使用 wiki-lint 检查当前 Wiki：raw 做基础检查，Wiki 按已确认的六类要求核对。 |
| 仅机械检查 | 使用 wiki-lint 只检查文件、链接、锚点和导航。 |

查询交付结果与建议，并向 `query-feedback/` 新增独立日志；不读取 raw，不修改知识、导航、SELF、规范或 Skill。需要保存新知识时另行使用 ingest，审核与修复按对应明确范围处理。

### 在其他项目中使用 Wiki

初始化会将查询 Skill 定制为 `query-quant-wiki` 这样的名称：Wiki 内保存本体，确认的共享 Skill 目录保存同名、同内容的镜像。Skill 绑定 Wiki 的绝对位置，外部项目沿 SELF、INDEX、定向搜索及知识页链接查询，无需把项目放进 Wiki 仓库。安装位置根据模型运行环境确定；Codex 的用户级共享目录见[官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。模板本身保留通用 `wiki-query`，不为尚未初始化的主题安装镜像。

例如，在使用方项目中请求：

```text
使用 query-quant-wiki 查找与当前问题有关的知识，读取正文后说明依据和适用条件。
只查询 wiki/，不读取 raw；向 query-feedback/ 新增本次反馈，不修改其他 Wiki 文件。
```

反馈记录查询时间与 Wiki 标识、问题摘要、检索词、实际读取的页面和章节、查询结果、限制及具体建议。每次使用唯一文件名，不追加或覆盖已有日志；无法回传时输出日志并说明未写入。Wiki 维护端之后审核反馈，日志本身不授权修订内容。

初始化后，介绍、规范及查询 Skill 的本体与镜像保持固定。知识与导航更新不触发 Skill 修改或重装，query 每次读取当前入口。外部环境无法访问绑定位置时报告具体限制；同名安装内容不一致时保留已有文件并报告冲突，不自动覆盖。

lint 中的结构工具依赖 Python 3.9+ 标准库，可从项目根目录直接运行：

```bash
python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root .
python3 .agents/skills/wiki-lint/scripts/check_wiki.py --root . --paths wiki/SELF.md wiki/INDEX.md
```

结构工具输出 JSON，列出实际范围、错误、提醒和跳过项；加 `--strict` 可让提醒也返回失败。局部运行跳过全库导航可达性；脚本在 raw/ 中默认只扫描 raw/README.md，来源正文在明确指定时扫描，避免误判原文中的相对链接。支持范围见 [wiki-lint 设计](.agents/skills/wiki-lint/README.md#51-工具检查范围)。

完整的 lint 还由 Agent 查看 raw 的保存位置、三部分是否齐全且可读、来源是否清楚，并复用 review 核对 [Wiki 的六类检查项](wiki/README.md#检查约定)。这些结果不包含在脚本 JSON 或退出码中；报告分别说明工具与 AI 的实际覆盖、确定问题、待核疑点和建议。raw 日常不做逐段转录校对。

### 设计参考

- [Karpathy 的 LLM Wiki 原始说明](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：来源整合、持久知识页面、带依据的查询和持续维护。
- [wpzero/karpathy-llm-wiki](https://github.com/wpzero/karpathy-llm-wiki)：将 ingest、query 和 lint 整理为 Agent 工作流程的实现参考。
- [godstale/LLM-WiKi](https://github.com/godstale/LLM-WiKi)：将结构检查工具与 Agent 内容检查配合使用的实现参考。

本模板结合这些思路和自身约定设计流程：raw 保留来源，wiki 组织可独立阅读的知识，通过标准 Markdown 链接与 INDEX 建立阅读路径，用 Git 记录修改。具体分类、来源格式和解释深度在初始化时确定。

完整示例与入库边界修订的实施安排、验收方法和后续工具取舍见 [模板改进方案](docs/template-improvement-plan.md)，实际结果见 [示例验收](examples/llm-wiki-demo/README.md#实际验收结果)。
