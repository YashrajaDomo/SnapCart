import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import httpx

engine = create_engine("sqlite:///payments.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    order_id = Column(String, index=True)
    customer_id = Column(String)
    amount = Column(Float)
    method = Column(String)
    status = Column(String)
    created_at = Column(String)
Base.metadata.create_all(engine)

app = FastAPI(title="SnapKart Payment Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PaymentInput(BaseModel):
    orderId: str
    customerId: str = "guest"
    amount: float
    paymentMethod: str

@app.post("/api/v1/payments/process")
def process_payment(data: PaymentInput):
    db = SessionLocal()
    transaction_id = "TXN" + uuid.uuid4().hex[:10].upper()
    status = "COD Pending" if data.paymentMethod == "Cash on Delivery" else "Paid"
    payment = Payment(id=transaction_id,order_id=data.orderId,customer_id=data.customerId,amount=data.amount,method=data.paymentMethod,status=status,created_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(payment)
    db.commit()
    db.close()
    try:
        with httpx.Client(timeout=2.0) as client:
            client.patch(
                f"http://localhost:8003/api/v1/orders/{data.orderId}/payment",
                params={"status": status},
            )
            client.post(
                "http://localhost:8005/api/v1/notifications",
                json={
                    "orderId": data.orderId,
                    "customerId": data.customerId,
                    "title": "Payment confirmed",
                    "message": f"Your payment of ₹{data.amount} for order {data.orderId} was successful.",
                    "type": "payment_confirmed",
                } if status == "Paid" else {
                    "orderId": data.orderId,
                    "customerId": data.customerId,
                    "title": "Cash on delivery selected",
                    "message": f"Payment of ₹{data.amount} for order {data.orderId} will be collected at delivery.",
                    "type": "payment_pending",
                },
            )
    except httpx.HTTPError:
        pass
    return {"transactionId":transaction_id,"orderId":data.orderId,"amount":data.amount,"paymentMethod":data.paymentMethod,"status":status}

@app.get("/api/v1/payments")
def payments(orderId: str | None = None):
    db = SessionLocal()
    query = db.query(Payment)
    if orderId:
        query = query.filter_by(order_id=orderId)
    rows = query.all()
    return [{"transactionId":p.id,"orderId":p.order_id,"amount":p.amount,"paymentMethod":p.method,"status":p.status,"createdAt":p.created_at} for p in rows]
