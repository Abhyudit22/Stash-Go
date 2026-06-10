from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate


def create_product(db: Session, product: ProductCreate, user_id: int):
    """Create a product securely tied to the logged-in user"""
    # Removed manual ID calculation; the database will auto-increment safely.
    new_product = Product(
        sku=product.sku,
        name=product.name,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        quantity_left=product.quantity_left,
        user_id=user_id  # ← NEW: Binds the product to the user
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def get_all_products(db: Session, user_id: int):
    """Fetch only the products belonging to the logged-in user"""
    # ← NEW: Filtered by user_id
    return db.query(Product).filter(Product.user_id == user_id).all()


def get_product_by_id(db: Session, product_id: int, user_id: int):
    """Fetch a specific product, ensuring it belongs to the user"""
    # ← NEW: Filtered by user_id
    return db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()


def get_product_by_sku(db: Session, sku: str, user_id: int):
    """Fetch a product by SKU, ensuring it belongs to the user"""
    # ← NEW: Filtered by user_id
    return db.query(Product).filter(Product.sku == sku, Product.user_id == user_id).first()


def update_product(db: Session, product_id: int, product_data: ProductUpdate, user_id: int):
    # ← NEW: Pass user_id to ensure they can't update someone else's product
    product = get_product_by_id(db, product_id, user_id)

    if product is None:
        return None

    update_data = product_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int, user_id: int):
    # ← NEW: Pass user_id to ensure they can't delete someone else's product
    product = get_product_by_id(db, product_id, user_id)

    if product is None:
        return None

    db.delete(product)
    db.commit()

    return product


def increase_stock(db: Session, product_id: int, quantity: int, user_id: int):
    # ← NEW: Security check
    product = get_product_by_id(db, product_id, user_id)

    if product is None:
        return None

    product.quantity_left += quantity

    db.commit()
    db.refresh(product)

    return product


def decrease_stock(db: Session, product_id: int, quantity: int, user_id: int):
    # ← NEW: Security check
    product = get_product_by_id(db, product_id, user_id)

    if product is None:
        return None

    if product.quantity_left < quantity:
        return "not_enough_stock"

    product.quantity_left -= quantity

    db.commit()
    db.refresh(product)

    return product