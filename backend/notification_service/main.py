import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///notifications.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    order_id = Column(String)
    title = Column(String)
    message = Column(String)
    type = Column(String)
    read = Column(Integer, default=0)
    created_at = Column(String)
Base.metadata.create_all(engine)

app = FastAPI(title="SnapKart Notification Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class NotificationInput(BaseModel):
    orderId: str
    customerId: str = "guest"
    title: str
    message: str
    type: str

@app.post("/api/v1/notifications")
def create_notification(data: NotificationInput):
    db = SessionLocal()
    item = Notification(id=str(uuid.uuid4())[:8],customer_id=data.customerId,order_id=data.orderId,title=data.title,message=data.message,type=data.type,read=0,created_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(item)
    db.commit()
    result = {"id":item.id,"orderId":item.order_id,"title":item.title,"message":item.message,"type":item.type,"read":False,"createdAt":item.created_at}
    db.close()
    return result

@app.get("/api/v1/notifications")
def list_notifications(customerId: str = "guest"):
    db = SessionLocal()
    rows = db.query(Notification).filter_by(customer_id=customerId).order_by(Notification.created_at.desc()).all()
    return [{"id":n.id,"orderId":n.order_id,"title":n.title,"message":n.message,"type":n.type,"read":bool(n.read),"createdAt":n.created_at} for n in rows]
