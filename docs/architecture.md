# MiniMall 精简电商平台 · 架构设计文档

| 项 | 内容 |
|---|---|
| 版本 | v0.2（决策点已确认） |
| 日期 | 2026-08-14 |
| 状态 | 待评审（编码前可用） |
| 上游 | [docs/requirements.md](requirements.md) |

---

## 1. 总体架构

### 1.1 分层与依赖方向

```
HTTP 请求
  │
router（参数校验、鉴权、响应组装）    ← 不写业务逻辑
  │
service（业务逻辑、事务边界）          ← 状态机、防超卖、金额计算
  │
repository（数据访问，MVP 预留）       ← 复用/测试需要时抽取
  │
ORM models + SQLAlchemy session       ← MySQL
```

- 依赖方向：自上而下单向；schemas（Pydantic）作为契约贯穿 router/service。
- 模块间通过 service 调用，**禁止跨模块直连数据库**。

### 1.2 业务模块划分

| 模块 | 核心职责 |
|---|---|
| auth | 注册/登录、JWT 签发与校验、当前用户注入 |
| users | 用户资料、收货地址 |
| categories / products | 分类树、SPU/SKU、商品列表/详情 |
| cart | 购物车增删改查 |
| orders | 下单（事务）、状态机、取消 |
| inventory | 库存维护、扣减/回补（防超卖策略见 §3.2） |
| payments | 模拟支付、回调幂等 |
| search（后期） | ES 全文搜索 |

### 1.3 请求处理流程（下单示例）

router 校验参数与鉴权 → service 开启事务 → 校验商品在售/库存充足 → 扣减库存 → 生成订单与明细 → 提交事务 → 返回订单号。任一步失败整体回滚。

---

## 2. 技术落地选型

| 项 | 选型 | 说明 |
|---|---|---|
| ORM / 迁移 | SQLAlchemy 2.0（同步）+ Alembic | **已定：同步（决策点 1）** |
| DB 驱动 | PyMySQL | 随同步选型 |
| 鉴权 | JWT（PyJWT） | 单 access token，MVP 无 refresh（已定） |
| Redis 客户端 | redis-py | 热商品缓存、浏览计数；购物车用 MySQL（决策点 3） |
| 配置 | pydantic-settings（已有） | 扩展 DB_URL、REDIS_URL、JWT 密钥等 |
| 依赖注入 | FastAPI Depends | `get_db` / `get_redis` / `get_current_user` |

---

## 3. 关键设计

### 3.1 订单状态机

- 枚举：`PENDING(待支付) → PAID(已支付) → SHIPPED(已发货) → COMPLETED(已完成)`；`CANCELED(已取消)`。
- 允许迁移（白名单）定义在 service 层常量；所有状态变更走统一方法校验迁移合法性，非法迁移抛 `AppError`。
- 字段：`orders.status`；可选 `order_status_log` 记录变更轨迹。

### 3.2 库存防超卖（已定：DB 条件更新）

- 扣减：`UPDATE inventory SET available = available - :n WHERE sku_id = :s AND available >= :n`，影响行数为 1 才成功，否则抛"库存不足"。
- 天然原子（行锁保证），无超卖；取消/退款时 `available = available + :n` 回补。
- 下单与扣库存在同一事务内；库存表与商品 SKU 一一对应。
- 若未来出现秒杀级流量，再评估 Redis 预扣（当前不引入）。

### 3.3 订单号生成（已定：时间戳 + 随机）

- 格式：`ORD + yyyyMMddHHmmss + 6 位随机数字`，如 `ORD20260814153012938472`。
- 可读、近似按时间有序、零外部依赖；随机后缀 + 唯一索引兜底防碰撞。

### 3.4 统一响应 / 异常 / 日志 / 配置

- **错误**：统一 `{"code","message"}`（AppError 已实现）；未捕获异常 → `500 INTERNAL_ERROR`。
- **成功**：直接返回业务数据，不做统一成功包装（减少样板）；分页统一 `{items, total, page, page_size}`。
- **日志**：`app/core/logging.py` 统一格式；service 关键路径 INFO，异常 ERROR。
- **配置**：`app/core/config.py` 扩展数据库/Redis/鉴权配置；`.env` 管理、不入库。

### 3.5 事务边界

- 下单为一个事务：扣库存 + 建订单 + 写明细，任一步失败整体回滚。
- service 层管理 session 提交/回滚；repository 层不持有事务逻辑（预留）。

### 3.6 购物车存储（已定：MySQL 表）

- `cart_items` 表：`user_id + sku_id + quantity`，唯一约束 `(user_id, sku_id)`。
- 加购时校验在售与库存；下单时以商品当前单价快照写入订单明细，随后清空对应购物车项。
- 不做 Redis 缓存（持久可靠优先，本项目规模收益小）。

---

## 4. 测试策略

| 层级 | 内容 | 依赖 |
|---|---|---|
| 单元 | 纯业务逻辑（状态机迁移、金额计算） | 无 DB/网络 |
| 集成 | service/repository + 真实 MySQL 测试库 | MySQL 测试库；Redis 用真实实例或 fakeredis |
| API | FastAPI TestClient，覆盖"注册→下单→支付"全链路 | 依赖覆盖 `get_db` 指向测试库 |

- **测试数据库**：本地 MySQL 独立测试库（本机无 Docker，不用 SQLite，因其行为与 MySQL 有差异）。
- **覆盖率**：核心业务（订单/库存/鉴权）≥ 80%。

---

## 5. 架构风险与待决策点

### 5.1 风险

| 风险 | 缓解 |
|---|---|
| Elasticsearch 未安装 | 搜索后置，MVP 用 SQL 兜底 |
| Redis 5.0 版本较老 | 训练够用；需要新特性时再升级 |
| Python 3.14 较新 | 已装依赖通过；新增依赖注意兼容 |
| Docker 未安装 | CI/CD 用 GitHub Actions；Docker 化延后 |

### 5.2 决策记录（2026-08-14 已确认）

| # | 决策点 | 决定 | 原因 |
|---|---|---|---|
| 1 | ORM 同步/异步 | **同步** | 简单易调试易测试；本项目规模不需要异步收益 |
| 2 | 库存防超卖 | **DB 条件更新** | 原子强一致，满足并发 100 不超卖；Redis 预扣复杂度高 |
| 3 | 购物车存储 | **MySQL 表** | 持久可靠可查询；Redis 收益小 |
| 4 | 订单号 | **时间戳+随机** | 可读近似有序、零外部依赖 |

> 其他已定：JWT 单 access token（30 分钟过期，无 refresh）；成功响应不统一包装、错误统一 `{code,message}`。
