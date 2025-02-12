from sqlmodel import Session
from fastapi import HTTPException,Depends,Query
from typing import List,Optional

from pro_1.models.Schemas import Cart,User,Product,CartCreate,CartItemOut
# Service to add a product to the cart
def add_to_cart(
    cart_data: Optional[CartCreate] = None, 
    db: Session = Depends(), 
    user_id: Optional[int] = Query(None), 
    product_id: Optional[int] = Query(None), 
    quantity: Optional[int] = Query(1)
) -> Cart:
    """
    Add product to cart using either query parameters or request body.
    If both are provided, query parameters take precedence.
    """

    # Use query params if provided, otherwise fallback to body request
    if user_id and product_id:
        cart_info = CartCreate(user_id=user_id, product_id=product_id, quantity=quantity)
    elif cart_data:
        cart_info = cart_data
    else:
        raise HTTPException(status_code=400, detail="Missing cart details in request")

    # Check if the user exists
    user = db.query(User).filter(User.id == cart_info.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the product exists
    product = db.query(Product).filter(Product.id == cart_info.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if item already exists in the cart
    existing_cart_item = db.query(Cart).filter(
        Cart.user_id == cart_info.user_id, 
        Cart.product_id == cart_info.product_id
    ).first()

    if existing_cart_item:
        existing_cart_item.quantity += cart_info.quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    else:
        db_cart_item = Cart(
            user_id=cart_info.user_id,
            product_id=cart_info.product_id,
            quantity=cart_info.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item



# Service to fetch all cart items for a specific user
def get_cart_items(
    db: Session, 
    user_id: int = Query(...)
) -> List[CartItemOut]:
    """
    Get cart items for a specific user using query parameters.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="No cart items found for this user")

    result = []
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        cart_item_out = CartItemOut(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=product.name,
            product_price=product.price
        )
        result.append(cart_item_out)

    return result





# Service to remove an item from the cart
def remove_cart_item(
    db: Session,
    user_id: int,
    product_id: int
):
    """
    Remove a product from the cart based on user_id and product_id.
    """
    cart_item = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item removed successfully"}



# Service to update cart item quantity (increase or decrease)
def update_cart_item(
    db: Session,
    user_id: int,
    product_id: int,
    quantity: int
) -> Cart:
    """
    Update the quantity of a cart item. If quantity is 0 or less, remove the item.
    """
    cart_item = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return {"message": "Cart item removed due to zero quantity"}

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item