# Wiki 通用模板

本项目的目的是帮助一个用户完成 Wiki 的初始化。项目提供通用文件与目录模板，并通过 `wiki-init` Skill 将模板定制为用户自己的 Wiki。

## 开始使用

1. 克隆模板仓库，在自己的本地副本中打开 Agent。
2. 使用 [wiki-init](.agents/skills/wiki-init/SKILL.md)，说明 Wiki 的用途、主题和已有资料。
3. 与 Agent 确定定位和组织方案，由 Agent 完成文件定制并检查结果。

可以这样开始：

```text
请使用 .agents/skills/wiki-init/SKILL.md 初始化当前 Wiki。
我希望用它整理……，主要用于……。
我已有的资料是……。
请先和我讨论定位、范围和目录安排，再完成已确定的方案。
```

没有初始资料时，也可以先完成目录与工作约定的初始化。

## 目录与文件

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
        └── wiki-init/
            └── SKILL.md       初始化方法
```

`raw/` 保存可追溯的来源，`wiki/` 组织经过理解的知识。具体分类由用户需求决定，有实际内容时再建立相应目录。

## 初始化后的入口

- 查看定位和当前状态：[wiki/SELF.md](wiki/SELF.md)。
- 浏览知识：[wiki/INDEX.md](wiki/INDEX.md)。
- 保存来源资料：[raw/README.md](raw/README.md)。
- 编写与维护知识页面：[wiki/README.md](wiki/README.md)。
- 了解 Agent 的工作约定：[AGENTS.md](AGENTS.md)。

初始化后，本文件应介绍用户自己的 Wiki；定位、范围和当前画像由 `wiki/SELF.md` 持续维护。
