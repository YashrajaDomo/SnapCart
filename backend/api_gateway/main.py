from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="SnapKart API Gateway")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SERVICES = {
    "catalog": "http://localhost:8001",
    "cart": "http://localhost:8002",
    "orders": "http://localhost:8003",
    "payments": "http://localhost:8004",
    "notifications": "http://localhost:8005",
    "ai": "http://localhost:8006",
}

async def proxy(request: Request, service: str, path: str):
    target = SERVICES[service] + path
    if request.url.query:
        target += "?" + request.url.query
    body = await request.body()
    headers = {"content-type": request.headers.get("content-type", "application/json")}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(request.method, target, content=body, headers=headers)
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(504, f"{service.title()} service timed out")
    except httpx.HTTPError:
        raise HTTPException(503, f"{service.title()} service is unavailable")

@app.api_route("/api/v1/catalog/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def catalog(request: Request, path: str):
    return await proxy(request, "catalog", "/api/v1/catalog/" + path)

@app.api_route("/api/v1/cart/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def cart(request: Request, path: str):
    return await proxy(request, "cart", "/api/v1/cart/" + path)

@app.api_route("/api/v1/cart", methods=["GET","POST","PATCH","DELETE"])
async def cart_root(request: Request):
    return await proxy(request, "cart", "/api/v1/cart")

@app.api_route("/api/v1/orders/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def orders(request: Request, path: str):
    return await proxy(request, "orders", "/api/v1/orders/" + path)

@app.api_route("/api/v1/orders", methods=["GET","POST","PATCH","DELETE"])
async def orders_root(request: Request):
    return await proxy(request, "orders", "/api/v1/orders")

@app.api_route("/api/v1/payments/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def payments(request: Request, path: str):
    return await proxy(request, "payments", "/api/v1/payments/" + path)

@app.api_route("/api/v1/payments", methods=["GET","POST","PATCH","DELETE"])
async def payments_root(request: Request):
    return await proxy(request, "payments", "/api/v1/payments")

@app.api_route("/api/v1/notifications/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def notifications(request: Request, path: str):
    return await proxy(request, "notifications", "/api/v1/notifications/" + path)

@app.api_route("/api/v1/notifications", methods=["GET","POST","PATCH","DELETE"])
async def notifications_root(request: Request):
    return await proxy(request, "notifications", "/api/v1/notifications")

@app.api_route("/api/v1/ai/{path:path}", methods=["GET","POST","PATCH","DELETE"])
async def ai(request: Request, path: str):
    return await proxy(request, "ai", "/api/v1/ai/" + path)
