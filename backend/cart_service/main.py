from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///cart.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, index=True)
    product_id = Column(Integer)
    name = Column(String)
    image = Column(String)
    price = Column(Float)
    quantity = Column(Integer, default=1)
Base.metadata.create_all(engine)

app = FastAPI(title="SnapKart Cart Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class CartInput(BaseModel):
    customerId: str = "guest"
    productId: int
    name: str
    image: str
    price: float
    quantity: int = 1

@app.post("/api/v1/cart/items")
def add_item(item: CartInput):
    db = SessionLocal()
    existing = db.query(CartItem).filter_by(customer_id=item.customerId, product_id=item.productId).first()
    if existing:
        existing.quantity += item.quantity
    else:
        db.add(CartItem(customer_id=item.customerId,product_id=item.productId,name=item.name,image=item.image,price=item.price,quantity=item.quantity))
    db.commit()
    db.close()
    return get_cart(item.customerId)

@app.get("/api/v1/cart")
def get_cart(customerId: str = "guest"):
    db = SessionLocal()
    rows = db.query(CartItem).filter_by(customer_id=customerId).all()
    items = [{"id":r.id,"productId":r.product_id,"name":r.name,"image":r.image,"price":r.price,"quantity":r.quantity} for r in rows]
    subtotal = round(sum(r["price"]*r["quantity"] for r in items),2)
    delivery = 0 if subtotal >= 499 or subtotal == 0 else 40
    db.close()
    return {"customerId":customerId,"items":items,"subtotal":subtotal,"delivery":delivery,"total":round(subtotal+delivery,2)}

@app.patch("/api/v1/cart/items/{item_id}")
def update_quantity(item_id: int, quantity: int):
    db = SessionLocal()
    item = db.query(CartItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(404,"Cart item not found")
    item.quantity = max(1,quantity)
    db.commit()
    customer_id = item.customer_id
    db.close()
    return get_cart(customer_id)

@app.delete("/api/v1/cart/items/{item_id}")
def remove_item(item_id: int):
    db = SessionLocal()
    item = db.query(CartItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(404,"Cart item not found")
    customer_id = item.customer_id
    db.delete(item)
    db.commit()
    db.close()
    return get_cart(customer_id)

@app.delete("/api/v1/cart")
def clear_cart(customerId: str = "guest"):
    db = SessionLocal()
    db.query(CartItem).filter_by(customer_id=customerId).delete()
    db.commit()
    db.close()
    return get_cart(customerId)
