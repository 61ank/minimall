"""开发用种子数据：分类、商品、SKU、库存。

运行：python -m app.seed
"""
from decimal import Decimal

from app.core.database import SessionLocal
from app.models import Category, Inventory, Product, Sku

SEED = [
    ("电子产品", [
        ("智能手机 X", [("星空黑 128G", "2999.00"), ("星光白 256G", "3299.00")]),
        ("蓝牙耳机", [("黑色 标准版", "199.00")]),
    ]),
    ("服饰", [
        ("纯棉T恤", [("白色 M", "59.00"), ("白色 L", "59.00")]),
    ]),
    ("家居生活", [
        ("保温杯", [("黑色 500ml", "89.00")]),
    ]),
]


def run() -> None:
    db = SessionLocal()
    try:
        for category_name, products in SEED:
            category = Category(name=category_name)
            db.add(category)
            db.flush()
            for product_name, skus in products:
                product = Product(name=product_name, category_id=category.id, status=1)
                db.add(product)
                db.flush()
                for idx, (sku_name, price) in enumerate(skus, start=1):
                    sku = Sku(
                        product_id=product.id,
                        sku_code=f"{product_name}-{idx}",
                        name=sku_name,
                        price=Decimal(price),
                        status=1,
                    )
                    db.add(sku)
                    db.flush()
                    db.add(Inventory(sku_id=sku.id, available=100))
        db.commit()
        print("种子数据插入完成")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
