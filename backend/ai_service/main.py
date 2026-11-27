import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)
app = FastAPI(title="SnapKart AI Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatInput(BaseModel):
    message: str
    customerId: str = "guest"

def is_support_query(text):
    return any(word in text.lower() for word in ["order","track","cancel","payment","delay","missing","customer support","contact","refund"])

def fallback_answer(message, products, orders):
    text = message.lower()
    if "track" in text or ("where" in text and "order" in text):
        if not orders:
            return "I could not find an order under this session. Please place an order or share your order ID."
        order = orders[0]
        return f"Your latest order {order['id']} is currently '{order['status']}'. It was placed on {order['createdAt']}."
    if "cancel" in text:
        return "You can cancel an eligible order from the Orders page before it reaches Out for Delivery or Delivered."
    if "payment" in text:
        return "SnapKart supports Cash on Delivery, UPI and Debit/Credit Card. UPI and cards are simulated in this demo."
    if "missing" in text:
        return "Please open the Notifications or Orders section and report the missing item with your order ID. Our demo support team will help you."
    if "contact" in text or "support" in text:
        return "For customer support, keep your order ID ready and use SnapKart support at support@snapkart.demo. This is a demo application."
    selected = [p for p in products if p["stock"] > 0]
    if "under" in text:
        import re
        match = re.search(r"(?:under|below)\s*₹?\s*(\d+)", text)
        if match:
            limit = int(match.group(1))
            selected = [p for p in selected if p["sellingPrice"] <= limit][:5]
    elif "snack" in text or "breakfast" in text:
        selected = [p for p in selected if ("Snacks" in p["category"] or p["name"] in ["Amul Taaza Homogenised Milk","Mother Dairy Fresh Curd","Britannia Whole Wheat Bread","Banana Robusta"])][:6]
    else:
        selected = selected[:6]
    if not selected:
        return "I could not find matching products in the available catalog. Please try another requirement."
    names = ", ".join(f"{p['name']} (₹{p['sellingPrice']})" for p in selected)
    return f"Here are some available options: {names}. You can add them to your cart directly."

@app.post("/api/v1/ai/chat")
async def chat(data: ChatInput):
    products, orders = [], []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            product_response = await client.get("http://localhost:8001/api/v1/catalog/products")
            products = product_response.json()
            order_response = await client.get("http://localhost:8003/api/v1/orders", params={"customerId":data.customerId})
            orders = order_response.json()
    except httpx.HTTPError:
        pass

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            context = "Use only this catalog and order data. Catalog: " + str(products[:20]) + ". Orders: " + str(orders[:5])
            response = client.models.generate_content(model="gemini-3.5-flash-lite", contents=f"{context}\nCustomer: {data.message}", config=types.GenerateContentConfig(temperature=0.5))
            if response.text:
                return {"reply":response.text,"products":[],"provider":"gemini"}
            logger.warning("Gemini returned an empty response; using local fallback")
        except Exception as error:
            logger.warning("Gemini request failed (%s); using local fallback", type(error).__name__)
    else:
        logger.info("GEMINI_API_KEY is not configured; using local fallback")
    return {
        "reply":fallback_answer(data.message,products,orders),
        "products": products[:6] if "recommend" in data.message.lower() or "suggest" in data.message.lower() else [],
        "provider":"local_fallback",
    }
