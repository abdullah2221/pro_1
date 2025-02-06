from sqlmodel import SQLModel, Field
from datetime import datetime

# class Product(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     name: str
#     description: str
#     price: float
#     created_by: str  # This field will just be a string, no foreign key reference
#     created_at: datetime = Field(default_factory=datetime.utcnow)  # Pass the function, not the result
#     updated_at: datetime = Field(default_factory=datetime.utcnow)  # Pass the function here too


# from sqlmodel import SQLModel, Field, Relationship
# from datetime import datetime
# from typing import Optional, List


# # Category Model
# class Category(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     parent_id: Optional[int] = Field(default=None, foreign_key="category.id")


# # Product Model
# class Product(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     description: str
#     price: float
#     created_by: str  # 'super_admin' or 'simple_admin'
#     category_id: Optional[int] = Field(default=None, foreign_key="category.id")
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)


# Inventory Management

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


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



    class Config:
        from_attributes = True
