# SnapKart

SnapKart is a beginner-friendly quick-commerce demo built with React, Vite, FastAPI and SQLite. It demonstrates independent microservices, API gateway routing, synchronous HTTP communication, a simple event-style order workflow, and Gemini-powered chat with a local fallback.

## Architecture

- React/Vite frontend — port 5173
- API Gateway — port 8000
- Catalog Service — port 8001
- Cart Service — port 8002
- Order Service — port 8003
- Payment Service — port 8004
- Notification Service — port 8005
- AI Service — port 8006

Each service owns a separate SQLite database and exposes Swagger at `/docs`.

## Run the application

### 1. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### 2. Backend

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Start each service in a separate terminal:

```powershell
cd backend/catalog_service && uvicorn main:app --port 8001
cd backend/cart_service && uvicorn main:app --port 8002
cd backend/order_service && uvicorn main:app --port 8003
cd backend/payment_service && uvicorn main:app --port 8004
cd backend/notification_service && uvicorn main:app --port 8005
cd backend/ai_service && uvicorn main:app --port 8006
cd backend/api_gateway && uvicorn main:app --port 8000
```

The gateway must start last and must be reachable before the frontend can communicate with the services.

## Gemini configuration

Copy `backend/.env.example` to `backend/.env` and set `GEMINI_API_KEY`. The AI service loads this file at startup and uses the Gemini 3.5 Flash-Lite model. Restart the AI service after changing the key. If Gemini or the key is unavailable, the chatbot falls back to local answers.

## Start everything with PowerShell

For local development, run:

```powershell
.\start_all.ps1
```

This script starts the API Gateway and all independent FastAPI services, then starts the Vite frontend. Stop the processes with the Stop button in each terminal or close the terminal windows.

## Demonstration workflow

1. Browse or search products.
2. Add products to the cart.
3. Open cart and change quantities.
4. Checkout and select a payment method.
5. Place the order.
6. Open Orders to track status or cancel an eligible order.
7. Open Notifications to view updates.
8. Use SnapKart AI for product suggestions and support.

## API examples

- `GET /api/v1/catalog/products`
- `GET /api/v1/catalog/products?search=milk`
- `GET /api/v1/cart?customerId=guest`
- `POST /api/v1/cart/items`
- `POST /api/v1/orders`
- `GET /api/v1/orders?customerId=guest`
- `POST /api/v1/payments/process`
- `GET /api/v1/notifications?customerId=guest`
- `POST /api/v1/ai/chat`
