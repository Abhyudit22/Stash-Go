from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate


def create_product(db: Session, product: ProductCreate):
    # Get the last product ID
    last_product = db.query(Product).order_by(Product.id.desc()).first()
    
    # Calculate next ID
    if last_product:
        next_id = last_product.id + 1
    else:
        next_id = 1
    
    # Create product with sequential ID
    new_product = Product(
        id=next_id,  # Manually set ID
        sku=product.sku,
        name=product.name,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        quantity_left=product.quantity_left
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def get_all_products(db: Session):
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str):
    return db.query(Product).filter(Product.sku == sku).first()


def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    update_data = product_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    db.delete(product)
    db.commit()

    return product


def increase_stock(db: Session, product_id: int, quantity: int):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    product.quantity_left += quantity

    db.commit()
    db.refresh(product)

    return product


def decrease_stock(db: Session, product_id: int, quantity: int):
    product = get_product_by_id(db, product_id)

    if product is None:
        return None

    if product.quantity_left < quantity:
        return "not_enough_stock"

    product.quantity_left -= quantity

    db.commit()
    db.refresh(product)

    return product