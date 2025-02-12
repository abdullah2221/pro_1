from fastapi import APIRouter, HTTPException, Body, Depends, Query,status
from pro_1.services.product_service import create_product, get_all_products, update_product, delete_product

from pro_1.config.db import Session, connection
# Import check_role function
from pro_1.utils.auth import check_role, check_role_factory
from pro_1.config.db import get_session
from pro_1.models.Schemas import Product,Category

import datetime
from fastapi.responses import JSONResponse
from typing import Optional
from sqlmodel import Session, select
router = APIRouter()

# ------------------- PRODUCT MANAGEMENT ENDPOINTS -------------------

# Add a product (Super Admin only)
# @router.post("/products")
# async def add_product(
#     name: str = Body(..., embed=True),
#     category: str = Body(..., embed=True),
#     price: float = Body(..., embed=True),
#     description:str = Body(...,embed=True),
#     created_by:int = Body(...,embed=True),
# ):
#     """
#     Add a product (No backend role check, only frontend enforces role).
#     """

#     if not name or not category or not price:
#         raise HTTPException(status_code=400, detail="All fields are required.")

#     with Session(connection) as session:
#         new_product = Product(name=name, category=category, price=price,description=description,created_by=created_by)
#         session.add(new_product)
#         session.commit()

#         return {"message": "Product added successfully", "product": new_product}

# # Fetch all products (Super Admin and Simple Admin can view)
# @router.get("/products", response_model=list[Product], dependencies=[Depends(check_role_factory("super_admin"))])
# async def fetch_all_products(session: Session = Depends(get_session)):
#     """Fetch all products (Super Admin or Simple Admin can view)."""
#     return get_all_products(session)

# # Update a product (Simple Admin only)
# @router.put("/update_product/{product_id}", dependencies=[Depends(check_role_factory("simple_admin"))])
# async def update_product_route(
#     product_id: int,
#     product_data: dict = Body(...),
# ):
#     """Update product details (Simple Admin only)."""
#     product_name = product_data.get("name")
#     product_category = product_data.get("category")
#     product_price = product_data.get("price")

#     if not product_name or not product_category or not product_price:
#         raise HTTPException(status_code=400, detail="Product name, category, and price are required.")

#     updated_product = update_product(product_id, product_name, product_category, product_price)
#     if updated_product:
#         return {"message": f"Product {product_id} updated successfully", "product": updated_product}
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")

# # Delete a product (Simple Admin only)
# @router.delete("/delete_product/{product_id}", dependencies=[Depends(check_role_factory("simple_admin"))])
# async def delete_product_route(
#     product_id: int,
# ):
#     """Delete a product (Simple Admin only)."""
#     deleted_product = delete_product(product_id)
#     if deleted_product:
#         return {"message": f"Product {product_id} deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")



# new data



# Create Product
@router.post("/products/", response_model=Product)
def create_product(
    product: Product, db: Session = Depends(get_session)
):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# Get All Products
@router.get("/products/", response_model=list[Product])
def get_products(db: Session = Depends(get_session)):
    products = db.exec(select(Product)).all()
    return products

# Get Product by ID
@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_session)):
    product = db.exec(select(Product).where(Product.id == product_id)).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product

# Update Product
@router.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int, product: Product, db: Session = Depends(get_session)
):
    # Fetch the existing product
    db_product = db.exec(select(Product).where(Product.id == product_id)).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Update product details (excluding 'created_by')
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.category_id = product.category_id
    db_product.updated_at = datetime.utcnow()  # Ensure this gets the proper timestamp

    # Commit the changes to the database
    db.commit()
    db.refresh(db_product)

    return db_product

# Delete Product
@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_session)):
    product = db.exec(select(Product).where(Product.id == product_id)).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    db.delete(product)
    db.commit()
    return {"msg": "Product deleted successfully"}

@router.post("/categories/",response_model=Category)
def create_category(category: Category, db: Session = Depends(get_session)):
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/categories/",response_model=list[Category])
def get_categories(db: Session = Depends(get_session)):
    categories = db.exec(select(Category)).all()
    return categories   