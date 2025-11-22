import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Restaurant, MenuItem, Order, OrderItem

app = FastAPI(title="Celestial Bites API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Celestial Bites API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Utility to convert ObjectId to string in responses

def serialize_doc(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

# Seed minimal demo data if collections are empty
@app.post("/seed")
def seed_data():
    try:
        if db["restaurant"].count_documents({}) == 0:
            rid1 = create_document("restaurant", Restaurant(name="Nebula Noodles", cuisine="Asian Fusion", rating=4.8, delivery_time_min=25, image_url="https://images.unsplash.com/photo-1540189549336-e6e99c3679fe").model_dump())
            rid2 = create_document("restaurant", Restaurant(name="Galaxy Grill", cuisine="BBQ", rating=4.6, delivery_time_min=30, image_url="https://images.unsplash.com/photo-1550547660-d9450f859349").model_dump())
            # Menu for rid1
            create_document("menuitem", MenuItem(restaurant_id=rid1, name="Supernova Ramen", description="Rich broth, cosmic umami", price=14.5, image_url="https://images.unsplash.com/photo-1544025162-d76694265947", tags=["spicy"]).model_dump())
            create_document("menuitem", MenuItem(restaurant_id=rid1, name="Stellar Gyoza", description="Crispy edges, juicy core", price=8.0, image_url="https://images.unsplash.com/photo-1604909052612-3f18102749a4", tags=["vegan"]).model_dump())
            # Menu for rid2
            create_document("menuitem", MenuItem(restaurant_id=rid2, name="Comet Brisket", description="12h slow-smoked", price=18.0, image_url="https://images.unsplash.com/photo-1553163147-622ab57be1c7").model_dump())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RESTAURANTS
@app.get("/restaurants")
def list_restaurants():
    docs = get_documents("restaurant")
    return [serialize_doc(d) for d in docs]

@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    try:
        doc = db["restaurant"].find_one({"_id": ObjectId(restaurant_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return serialize_doc(doc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

# MENU
@app.get("/restaurants/{restaurant_id}/menu")
def get_menu(restaurant_id: str):
    docs = get_documents("menuitem", {"restaurant_id": restaurant_id})
    return [serialize_doc(d) for d in docs]

# ORDERS
class CreateOrderRequest(BaseModel):
    restaurant_id: str
    restaurant_name: str
    items: List[OrderItem]
    customer_name: str
    address: str
    phone: str
    notes: Optional[str] = None

@app.post("/orders")
def create_order(payload: CreateOrderRequest):
    # Calculate totals on the server to avoid tampering
    subtotal = sum(i.price * i.quantity for i in payload.items)
    delivery_fee = 3.99 if subtotal < 30 else 0.0
    total = round(subtotal + delivery_fee, 2)

    order = Order(
        restaurant_id=payload.restaurant_id,
        restaurant_name=payload.restaurant_name,
        items=payload.items,
        subtotal=round(subtotal, 2),
        delivery_fee=delivery_fee,
        total=total,
        customer_name=payload.customer_name,
        address=payload.address,
        phone=payload.phone,
        notes=payload.notes,
        status="placed"
    )
    oid = create_document("order", order.model_dump())
    return {"id": oid, "status": "placed", "total": total}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
