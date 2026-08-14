---
name: learning-project
description: 用户在 e:\code\cluade code project 的 Claude Code 全流程实战训练项目 — 阶段式推进方式、汇报格式、已定技术决策
metadata:
  type: project
---

用户在 `e:\code\cluade code project`（当前为完全空目录）运行一个 **Claude Code 全流程实战训练项目**，目标是系统学会 Claude Code 覆盖完整软件生命周期。

**工作方式（关键）：** 阶段式推进 `阶段 → 执行 → 汇报 → 用户反馈给 AI 教练 → 教练下指令 → 下一阶段`。Claude Code 只执行"当前明确阶段"，绝不一口气做完整个项目，也不提前创建业务功能。每次完成后按固定格式汇报：本阶段完成 / 修改的文件 / 执行的命令 / 验证结果 / 发现的问题 / 建议。**每轮汇报末尾，Claude 必须给出"下一条命令"**（一段可复制发送的 Prompt，让用户明确下一步做什么，用户会将此命令发送回来执行；2026-08-14 用户要求）。**训练日志**：每轮结束后把"本轮做了什么 + 对应意义（学到什么）"追加到 `docs/training-log.md`，供用户后续学习复习（2026-08-14 用户要求，用途是"方便后面学习"）。

**Why:** 用户的学习目标是把 Claude Code 当训练工具而非单纯代码生成器，每个决策点由用户或其 AI 教练拍板。

**How to apply:** 收到任何任务先判断属于哪个阶段，只推进当前阶段；多方案时给出推荐+权衡后等用户决定，不擅自替用户做学习决策；遵守最小必要修改原则；命令失败如实报告现象/原因/处理方案；删除、git reset 等危险操作先征询。

**记忆存放位置（2026-08-14 用户要求）：** 记忆文件统一存放在项目下 `.claude/memory/`，后续新增记忆一律写入此目录（本文件即其一）。待 CLAUDE.md 阶段需在 CLAUDE.md 中加入指向该目录的说明，确保未来会话能自动加载项目记忆。

**已定技术决策（2026-08-14）：**
- 项目题材：**精简电商平台（MiniMall）**，需求文档见 `docs/requirements.md`
- 技术栈：**Python + FastAPI**（用户明确想多学 Python；Django/Java Spring Boot 被否）
- Docker：**暂不安装**，CI/CD 用 GitHub Actions，Docker 化阶段延后
- 目标覆盖：需求分析、规划、探索、编码、测试、Debug、Review、重构、Git、CLAUDE.md、Skills、MCP、Redis/ES、AI/RAG、Docker、CI/CD、文档

**环境事实（2026-08-14 侦察）：** Python 3.14.7（另有 3.10）；JDK 21 + Maven 3.9.1；Git 2.45.1；MySQL 8.0.33 运行中(3306)；Redis 5.0.14 已装未运行(6379 未监听)；Elasticsearch 未安装；Docker 未安装。Windows 10，bash。
