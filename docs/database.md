# MiniMall 精简电商平台 · 数据库设计文档

| 项 | 内容 |
|---|---|
| 版本 | v0.1 |
| 日期 | 2026-08-14 |
| 状态 | 已定（决策：物理外键、复数 snake_case） |
| 上游 | [docs/requirements.md](requirements.md)、[docs/architecture.md](architecture.md) |

---

## 1. 设计约定

- **命名**：复数 snake_case（`users`、`cart_items`）；主键 `id BIGINT` 自增。
- **时间**：`created_at` / `updated_at` DATETIME，`updated_at` 自动随更新刷新。
- **外键**：物理外键（InnoDB），默认 `RESTRICT` 防误删被引用行。
- **字符集**：utf8mb4；金额用 `DECIMAL(10,2)`；状态字段存**可读字符串**（VARCHAR），以 Python Enum 定义、落库为 VARCHAR，便于演进。
- **软删除**：MVP 不引入（删除直接物理删除或仅下架，后续需要再加）。

## 2. 表清单与关系

```
users 1─N addresses              收货地址
users 1─N cart_items N─1 skus    购物车
categories 1─N products 1─N skus 1─1 inventory   商品与库存
users 1─N orders 1─N order_items N─1 skus        订单与明细（明细含快照）
orders 1─1 payment_records       模拟支付
```

| 表 | 说明 |
|---|---|
| users | 用户账号 |
| addresses | 收货地址（下单时快照到订单） |
| categories | 分类（树形，parent_id 自关联） |
| products | 商品 SPU（标题/描述/封面/销量） |
| skus | 商品规格 SKU（价格/规格名） |
| inventory | 库存（与 sku 一对一） |
| cart_items | 购物车项 |
| orders | 订单主表（含收货快照、金额、状态机） |
| order_items | 订单明细（价格/名称快照） |
| payment_records | 模拟支付记录 |

## 3. 表结构

### users
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| email | VARCHAR(100) | UNIQUE, NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| nickname | VARCHAR(50) | NULL | 昵称 |
| status | TINYINT | NOT NULL DEFAULT 1 | 1 正常 / 0 禁用 |
| created_at / updated_at | DATETIME | NOT NULL | |

### addresses
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| user_id | BIGINT | FK→users.id, NOT NULL | |
| receiver | VARCHAR(50) | NOT NULL | 收货人 |
| phone | VARCHAR(20) | NOT NULL | |
| province / city / district | VARCHAR(50) | NOT NULL | |
| detail | VARCHAR(200) | NOT NULL | 详细地址 |
| is_default | TINYINT | DEFAULT 0 | 1 默认 |
| created_at / updated_at | DATETIME | | |

### categories
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| name | VARCHAR(50) | NOT NULL, UNIQUE | |
| parent_id | BIGINT | FK→categories.id, NULL | 0/null 为根节点 |
| sort_order | INT | DEFAULT 0 | 排序 |
| created_at / updated_at | DATETIME | | |

### products
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| name | VARCHAR(200) | NOT NULL | SPU 名称 |
| description | TEXT | NULL | |
| category_id | BIGINT | FK→categories.id | |
| cover_image | VARCHAR(255) | NULL | |
| status | TINYINT | DEFAULT 1 | 1 上架 / 0 下架 |
| sales | INT | DEFAULT 0 | 销量（冗余，用于排序） |
| created_at / updated_at | DATETIME | | |

### skus
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| product_id | BIGINT | FK→products.id, NOT NULL | |
| sku_code | VARCHAR(50) | UNIQUE | 规格编码 |
| name | VARCHAR(100) | NOT NULL | 规格名（红/大） |
| price | DECIMAL(10,2) | NOT NULL | 售价 |
| status | TINYINT | DEFAULT 1 | 1 在售 / 0 停售 |
| created_at / updated_at | DATETIME | | |

### inventory
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| sku_id | BIGINT | FK→skus.id, UNIQUE | 与 sku 一对一 |
| available | INT | NOT NULL DEFAULT 0 | 可用库存（防超卖条件更新目标） |
| created_at / updated_at | DATETIME | | |

### cart_items
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| user_id | BIGINT | FK→users.id, NOT NULL | |
| sku_id | BIGINT | FK→skus.id, NOT NULL | |
| quantity | INT | NOT NULL DEFAULT 1 | |
| created_at / updated_at | DATETIME | | 唯一约束 (user_id, sku_id) |

### orders
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| order_no | VARCHAR(32) | NOT NULL, UNIQUE | 时间戳+随机 |
| user_id | BIGINT | FK→users.id, NOT NULL | |
| address_id | BIGINT | FK→addresses.id, NULL | 仅供参考，实际用快照 |
| receiver / phone / address | VARCHAR | NOT NULL | 收货快照 |
| total_amount | DECIMAL(10,2) | NOT NULL | 商品总额 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'PENDING' | 状态机（见 §5） |
| paid_at / shipped_at / completed_at / canceled_at | DATETIME | NULL | 各迁移时刻 |
| created_at / updated_at | DATETIME | | |

### order_items
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| order_id | BIGINT | FK→orders.id, NOT NULL | |
| sku_id | BIGINT | FK→skus.id, NOT NULL | 仅供参考，实际用快照 |
| product_name / sku_name | VARCHAR | NOT NULL | 名称快照 |
| price | DECIMAL(10,2) | NOT NULL | 单价快照 |
| quantity | INT | NOT NULL | |
| subtotal | DECIMAL(10,2) | NOT NULL | price × quantity |

### payment_records
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT | PK | |
| order_id | BIGINT | FK→orders.id, UNIQUE | 一单一支付 |
| pay_no | VARCHAR(64) | NOT NULL, UNIQUE | 支付流水号 |
| amount | DECIMAL(10,2) | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/SUCCESS/FAILED |
| channel | VARCHAR(20) | DEFAULT 'mock' | 模拟通道 |
| created_at / paid_at | DATETIME | | |

## 4. 索引设计（热点查询 → 索引）

| 热点查询 | 索引 |
|---|---|
| 商品列表按分类/状态筛选 | `products(category_id, status)` |
| 商品列表按销量/价格排序 | `products(sales)`、`skus(price)` |
| 下单按 SKU 条件更新库存（防超卖） | `inventory(sku_id)`（唯一） |
| 购物车按用户查 | `cart_items(user_id)`，唯一 `(user_id, sku_id)` |
| 订单按用户+时间查 | `orders(user_id, created_at)`；`orders(status)` |
| 订单明细 | `order_items(order_id)` |
| 地址按用户查 | `addresses(user_id)` |
| 支付回查 | `payment_records(order_id)`（唯一） |
| 商品/订单号精确查 | `products(id)`、`orders(order_no)`（唯一） |

## 5. 订单状态机落库

- `orders.status` VARCHAR(20)，取值与迁移：

```
PENDING(待支付) → PAID(已支付) → SHIPPED(已发货) → COMPLETED(已完成)
      └────────→ CANCELED(已取消)
```

- 合法迁移白名单在 service 层（阶段 7 实现）；对应迁移时刻写入 `paid_at` / `shipped_at` / `completed_at` / `canceled_at`。
- 支付记录 `payment_records.status`：`PENDING → SUCCESS`（失败置 `FAILED`）。

## 6. 种子数据

- 分类：电子产品、服饰、家居生活（各 1-2 个二级分类示例）。
- 商品：每分类 2 个 SPU，各含 1-2 个 SKU，`inventory.available` 各 100，价格不等，部分上架/下架以验证筛选。
