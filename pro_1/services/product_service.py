from sqlmodel import Session, select
from pro_1.models.Schemas import Product,Category
from typing import List

import datetime
from fastapi import HTTPException, status
# Create Product (Simple Admin can add)
# async def create_product(product: Product, db: Session):
#     db.add(product)
#     db.commit()
#     db.refresh(product)
#     return product


# # Get all products (Super Admin or Simple Admin can view)
# async def get_all_products(db: Session) -> List[Product]:
#     return db.exec(select(Product)).all()


# # Get products for client (based on product category or other logic)
# async def get_products_for_client(current_user, db: Session) -> List[Product]:
#     # Clients can view products based on assigned categories or other logic
#     return db.exec(select(Product).where(Product.category == "Professional")).all()


# # Get a product by ID
# async def get_product_by_id(product_id: int, db: Session) -> Product:
#     return db.get(Product, product_id)


# # Update a product
# async def update_product(product_id: int, updated_product: Product, db: Session) -> Product:
#     product = await get_product_by_id(product_id, db)
#     if product:
#         product.name = updated_product.name
#         product.description = updated_product.description
#         product.price = updated_product.price
#         product.category = updated_product.category
#         product.updated_at = updated_product.updated_at
#         db.commit()
#         db.refresh(product)
#         return product
#     else:
#         raise Exception("Product not found")


# # Delete a product
# async def delete_product(product_id: int, db: Session) -> Product:
#     product = await get_product_by_id(product_id, db)
#     if product:
#         db.delete(product)
#         db.commit()
#         return product
#     else:
#         raise Exception("Product not found")
    
    
    
    
# new data




def create_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_all_products(db: Session) -> list[Product]:
    return db.exec(select(Product)).all()

def get_product_by_id(db: Session, product_id: int) -> Product:
    return db.exec(select(Product).where(Product.id == product_id)).first()

def update_product(db: Session, product_id: int, product_data: Product) -> Product:
    db_product = db.exec(select(Product).where(Product.id == product_id)).first()
    if db_product:
        db_product.name = product_data.name
        db_product.description = product_data.description
        db_product.price = product_data.price
        db_product.created_by = product_data.created_by
        db_product.category_id = product_data.category_id
        db_product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_product)
        return db_product
    return None

def delete_product(db: Session, product_id: int) -> bool:
    db_product = db.exec(select(Product).where(Product.id == product_id)).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


def category(db:Session,category:Category):
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
