---
name: learning-project
description: 用户在 e:\code\cluade code project 的 Claude Code 全流程实战训练项目 — 阶段式推进方式、汇报格式、已定技术决策
metadata:
  type: project
---

用户在 `e:\code\cluade code project`（当前为完全空目录）运行一个 **Claude Code 全流程实战训练项目**，目标是系统学会 Claude Code 覆盖完整软件生命周期。

**工作方式（关键）：** 阶段式推进 `阶段 → 执行 → 汇报 → 用户反馈给 AI 教练 → 教练下指令 → 下一阶段`。Claude Code 只执行"当前明确阶段"，绝不一口气做完整个项目，也不提前创建业务功能。每次完成后按固定格式汇报：本阶段完成 / 修改的文件 / 执行的命令 / 验证结果 / 发现的问题 / 建议。**每轮汇报末尾，Claude 必须给出"下一条命令"**（一段可复制发送的 Prompt，让用户明确下一步做什么，用户会将此命令发送回来执行；2026-08-14 用户要求）。**训练日志**：每轮结束后把"本轮做了什么 + 对应意义（练到的 Claude Code 能力）"追加到 `docs/training-log.md`，供用户后续学习复习（2026-08-14 用户要求，用途是"方便后面学习"）。**对应意义硬性规则（2026-08-14 用户补充）**：必须回答两问——①"这个知识点不用 Claude Code 也能学到吗？"能→降为背景，不能→才是本轮重点；②"下次同类任务怎么驱动 Claude Code？"写成一句可复用指令。纯项目/框架知识降级为背景或并入"做了什么"。**每轮汇报以"本轮练到的 Claude Code 能力：…，以后同类任务这样驱动：…"收尾**。**Git 同步**：每轮全部文件修改完成后，统一执行一次 git 提交 + 推送（批量提交，不在修改过程中逐文件提交；2026-08-14 用户补充）。

**Why:** 用户的学习目标是把 Claude Code 当训练工具而非单纯代码生成器，每个决策点由用户或其 AI 教练拍板。

**How to apply:** 收到任何任务先判断属于哪个阶段，只推进当前阶段；多方案时给出推荐+权衡后等用户决定，不擅自替用户做学习决策；遵守最小必要修改原则；命令失败如实报告现象/原因/处理方案；删除、git reset 等危险操作先征询。

**记忆存放位置（2026-08-14 用户要求）：** 记忆文件统一存放在项目下 `.claude/memory/`，后续新增记忆一律写入此目录（本文件即其一）。待 CLAUDE.md 阶段需在 CLAUDE.md 中加入指向该目录的说明，确保未来会话能自动加载项目记忆。

**已定技术决策（2026-08-14）：**
- 项目题材：**精简电商平台（MiniMall）**，需求文档见 `docs/requirements.md`
- 技术栈：**Python + FastAPI**（用户明确想多学 Python；Django/Java Spring Boot 被否）
- 依赖管理：**requirements.txt**；虚拟环境 Python 3.14（2026-08-14 用户选择，均非项目默认）
- Docker：**暂不安装**，CI/CD 用 GitHub Actions，Docker 化阶段延后
- 目标覆盖：需求分析、规划、探索、编码、测试、Debug、Review、重构、Git、CLAUDE.md、Skills、MCP、Redis/ES、AI/RAG、Docker、CI/CD、文档

**环境事实（2026-08-14 侦察）：** Python 3.14.7（另有 3.10）；JDK 21 + Maven 3.9.1；Git 2.45.1；MySQL 8.0.33 运行中(3306)；Redis 5.0.14 已装未运行(6379 未监听)；Elasticsearch 未安装；Docker 未安装。Windows 10，bash。

**Git 远程（2026-08-14）：** GitHub 仓库 `https://github.com/61ank/minimall`（用户名 61ank），origin 已绑定并推送 main。gh CLI 未安装。

**项目上下文（2026-08-14）：** 项目根 `CLAUDE.md` 已创建，承载会话级项目上下文（结构/命令/规范/决策）；需求在 `docs/requirements.md`；训练日志在 `docs/training-log.md`；本记忆目录为 `.claude/memory/`。

**项目状态（2026-08-14）：** 手把手开发暂停于阶段九（核心交易闭环已完成可运行：鉴权/用户/商品/购物车/订单/库存/支付，18 个 API）。待学能力清单与详细教学已写入 `docs/training-log.md` 轮次 15，供后续自学/续学。
