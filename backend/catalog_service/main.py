from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///catalog.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String)
    category = Column(String)
    image = Column(String)
    quantity = Column(String)
    description = Column(String)
    mrp = Column(Float)
    selling_price = Column(Float)
    discount = Column(Float)
    stock = Column(Integer)

Base.metadata.create_all(engine)
app = FastAPI(title="SnapKart Catalog Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SAMPLE_PRODUCTS = [
("Amul Taaza Homogenised Milk","Amul","Dairy & Eggs","https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600","1 litre","Fresh toned milk",70,64,9,40),
("Mother Dairy Fresh Curd","Mother Dairy","Dairy & Eggs","https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600","400 g","Creamy set curd",40,36,10,35),
("Farm Fresh Eggs","Local Farms","Dairy & Eggs","https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=600","6 pcs","Protein-rich brown eggs",90,82,9,25),
("Britannia Whole Wheat Bread","Britannia","Bakery","https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600","400 g","Soft whole wheat bread",55,48,13,30),
("Banana Robusta","Fresh Farms","Fruits & Vegetables","https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600","1 kg","Naturally sweet ripe bananas",65,58,11,50),
("Red Apple","Shimla Orchards","Fruits & Vegetables","https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600","500 g","Crisp and juicy apples",180,149,17,45),
("Fresh Tomatoes","Farm Fresh","Fruits & Vegetables","https://images.unsplash.com/photo-1546094096-0df4bcaaa812?w=600","1 kg","Juicy red tomatoes",50,42,16,60),
("Potatoes","Farm Fresh","Fruits & Vegetables","https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600","1 kg","Versatile everyday potatoes",40,35,13,70),
("Lay's Classic Salted Chips","Lay's","Snacks","https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600","52 g","Classic crunchy potato chips",20,18,10,80),
("Cadbury Dairy Milk","Cadbury","Snacks","https://images.unsplash.com/photo-1548907040-4d42eba3865b?w=600","45 g","Smooth milk chocolate",60,54,10,50),
("Maggi 2-Minute Noodles","Maggi","Snacks","https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=600","280 g","Masala instant noodles",104,89,14,45),
("Bingo Mad Angles","Bingo","Snacks","https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600","130 g","Tangy spicy triangle chips",50,42,16,55),
("Coca-Cola","Coca-Cola","Beverages","https://images.unsplash.com/photo-1629203849820-fdd70d49c38e?w=600","750 ml","Refreshing cola drink",40,36,10,60),
("Minute Maid Mixed Fruit","Minute Maid","Beverages","https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=600","1 litre","Refreshing mixed fruit juice",110,99,10,35),
("Tata Tea Gold","Tata","Beverages","https://images.unsplash.com/photo-1594631661960-34762324f0ed?w=600","500 g","Rich and aromatic tea",325,280,14,30),
("Dove Beauty Bar","Dove","Personal Care","https://images.unsplash.com/photo-1607006483224-0286a5d0db6f?w=600","100 g","Moisturising beauty soap",85,72,15,40),
("Colgate MaxFresh Toothpaste","Colgate","Personal Care","https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600","150 g","Fresh mint toothpaste",145,119,18,35),
("Surf Excel Easy Wash","Surf Excel","Household Essentials","https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=600","1 kg","Powerful everyday detergent",220,189,14,30),
("Tissue Paper Roll","CleanHome","Household Essentials","https://images.unsplash.com/photo-1584556812952-905ffd0c611a?w=600","4 pcs","Soft kitchen tissue rolls",160,139,13,25),
("Dark Fantasy Cookies","Sunfeast","Bakery","https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600","300 g","Rich chocolate-filled cookies",120,105,13,38),
]

@app.on_event("startup")
def seed():
    db = SessionLocal()
    if db.query(Product).count() == 0:
        for row in SAMPLE_PRODUCTS:
            db.add(Product(name=row[0],brand=row[1],category=row[2],image=row[3],quantity=row[4],description=row[5],mrp=row[6],selling_price=row[7],discount=row[8],stock=row[9]))
        db.commit()
    db.close()

def to_dict(p):
    return {"id":p.id,"name":p.name,"brand":p.brand,"category":p.category,"image":p.image,"quantity":p.quantity,"description":p.description,"mrp":p.mrp,"sellingPrice":p.selling_price,"discount":p.discount,"stock":p.stock}

@app.get("/api/v1/catalog/products")
def products(search: str | None = Query(None), category: str | None = Query(None)):
    db = SessionLocal()
    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category and category != "All":
        query = query.filter(Product.category == category)
    return [to_dict(p) for p in query.all()]

@app.get("/api/v1/catalog/products/{product_id}")
def product_detail(product_id: int):
    db = SessionLocal()
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404,"Product not found")
    return to_dict(p)

@app.get("/api/v1/catalog/categories")
def categories():
    return ["Fruits & Vegetables","Dairy & Eggs","Snacks","Beverages","Personal Care","Household Essentials","Bakery"]

@app.post("/api/v1/catalog/products/{product_id}/reserve")
def reserve_product(product_id: int, quantity: int = 1):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.stock < quantity:
        raise HTTPException(409, f"Insufficient stock for {product.name}")
    product.stock -= quantity
    db.commit()
    result = to_dict(product)
    db.close()
    return result
