from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from typing import Optional, List

# User Model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    role_id: int = Field(default=None, foreign_key="role.id")

    # Relationship to Cart (we will add this)
    cart_items: List["Cart"] = Relationship(back_populates="user")

# Role Model
class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

# Category Model
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

    # Relationship to Products
    products: List["Product"] = Relationship(back_populates="category")

# Product Model
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    created_by: str  # 'super_admin' or 'simple_admin'
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to Category
    category: Optional[Category] = Relationship(back_populates="products")
    
    # Relationship to Cart (reverse relationship)
    carts: List["Cart"] = Relationship(back_populates="product")

    class Config:
        from_attributes = True

# Cart Model
class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: Optional[int] = Field(default=1)

    # Relationships (use string references)
    user: "User" = Relationship(back_populates="cart_items")
    product: "Product" = Relationship(back_populates="carts")

# Pydantic schemas for Cart operations

# Schema for adding a product to the cart
class CartCreate(SQLModel):
    user_id: int
    product_id: int
    quantity: Optional[int] = 1

# Schema for showing cart items for a user
class CartItemOut(SQLModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: float

    class Config:
        from_attributes = True

# Schema for showing all cart items for a specific user
class CartOut(SQLModel):
    user_id: int
    cart_items: List[CartItemOut]

    class Config:
        from_attributes = True
