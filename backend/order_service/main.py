import json, uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import httpx

engine = create_engine("sqlite:///orders.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    address = Column(String)
    items_json = Column(Text)
    subtotal = Column(Float)
    delivery = Column(Float)
    total = Column(Float)
    payment_method = Column(String)
    payment_status = Column(String, default="Pending")
    status = Column(String, default="Order Placed")
    created_at = Column(String)
Base.metadata.create_all(engine)

app = FastAPI(title="SnapKart Order Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderInput(BaseModel):
    customerId: str = "guest"
    address: str
    items: list[dict]
    subtotal: float
    delivery: float
    total: float
    paymentMethod: str

def serialize(order):
    return {"id":order.id,"customerId":order.customer_id,"address":order.address,"items":json.loads(order.items_json),"subtotal":order.subtotal,"delivery":order.delivery,"total":order.total,"paymentMethod":order.payment_method,"paymentStatus":order.payment_status,"status":order.status,"createdAt":order.created_at}

def dispatch_order_events(order_id: str, customer_id: str, amount: float, payment_method: str, items: list[dict]):
    try:
        with httpx.Client(timeout=2.0) as client:
            for item in items:
                product_id = item.get("productId") or item.get("id")
                quantity = item.get("quantity", 1)
                if product_id:
                    client.post(
                        f"http://localhost:8001/api/v1/catalog/products/{product_id}/reserve",
                        params={"quantity": quantity},
                    )
            client.post(
                "http://localhost:8004/api/v1/payments/process",
                json={
                    "orderId": order_id,
                    "customerId": customer_id,
                    "amount": amount,
                    "paymentMethod": payment_method,
                },
            )
            client.post(
                "http://localhost:8005/api/v1/notifications",
                json={
                    "orderId": order_id,
                    "customerId": customer_id,
                    "title": "Order confirmed",
                    "message": f"Your order {order_id} has been placed successfully.",
                    "type": "order_confirmed",
                },
            )
    except httpx.HTTPError:
        pass

@app.post("/api/v1/orders")
def place_order(data: OrderInput, background_tasks: BackgroundTasks):
    db = SessionLocal()
    order_id = "SK" + uuid.uuid4().hex[:8].upper()
    order = Order(id=order_id,customer_id=data.customerId,address=data.address,items_json=json.dumps(data.items),subtotal=data.subtotal,delivery=data.delivery,total=data.total,payment_method=data.paymentMethod,payment_status="Pending",status="Order Placed",created_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(order)
    db.commit()
    db.refresh(order)
    result = serialize(order)
    db.close()
    background_tasks.add_task(
        dispatch_order_events,
        order_id,
        data.customerId,
        data.total,
        data.paymentMethod,
        data.items,
    )
    return result

@app.get("/api/v1/orders")
def order_history(customerId: str = "guest"):
    db = SessionLocal()
    rows = db.query(Order).filter_by(customer_id=customerId).order_by(Order.created_at.desc()).all()
    return [serialize(r) for r in rows]

@app.get("/api/v1/orders/{order_id}")
def order_detail(order_id: str):
    db = SessionLocal()
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404,"Order not found")
    return serialize(order)

@app.post("/api/v1/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    db = SessionLocal()
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404,"Order not found")
    if order.status in ("Out for Delivery","Delivered","Cancelled"):
        raise HTTPException(400,"This order cannot be cancelled")
    order.status = "Cancelled"
    db.commit()
    result = serialize(order)
    db.close()
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post("http://localhost:8005/api/v1/notifications",json={"orderId":order_id,"customerId":"guest","title":"Order cancelled","message":f"Order {order_id} was cancelled.","type":"order_cancelled"})
    except httpx.HTTPError:
        pass
    return result

@app.patch("/api/v1/orders/{order_id}/status")
def update_status(order_id: str, status: str):
    db = SessionLocal()
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404,"Order not found")
    order.status = status
    db.commit()
    db.close()
    return order_detail(order_id)

@app.patch("/api/v1/orders/{order_id}/payment")
def update_payment_status(order_id: str, status: str):
    db = SessionLocal()
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    order.payment_status = status
    db.commit()
    db.close()
    return order_detail(order_id)
