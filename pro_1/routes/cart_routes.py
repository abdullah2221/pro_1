from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from pro_1.models.Schemas import CartCreate, CartOut
from pro_1.services import cart_service
from pro_1.config.db import get_session

router = APIRouter()

# Route to add a product to the cart (supports both body & query params)
@router.post("/cart/")
def add_to_cart(
    cart_data: Optional[CartCreate] = None,
    db: Session = Depends(get_session),
    user_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    quantity: Optional[int] = Query(1)
):
    return cart_service.add_to_cart(cart_data, db, user_id, product_id, quantity)


# Route to fetch cart items for a specific user (uses query parameter)
@router.get("/cart/", response_model=CartOut)
def get_cart(
    user_id: int = Query(...),
    db: Session = Depends(get_session)
):
    cart_items = cart_service.get_cart_items(db, user_id)
    return {"user_id": user_id, "cart_items": cart_items}
# Route to remove an item from the cart
@router.delete("/cart/")
def remove_cart_item(
    user_id: int = Query(...),
    product_id: int = Query(...),
    db: Session = Depends(get_session)
):
    return cart_service.remove_cart_item(db, user_id, product_id)


# Route to update the quantity of a cart item (increase or decrease)
@router.put("/cart/")
def update_cart_item(
    user_id: int = Query(...),
    product_id: int = Query(...),
    quantity: int = Query(...),
    db: Session = Depends(get_session)
):
    return cart_service.update_cart_item(db, user_id, product_id, quantity)