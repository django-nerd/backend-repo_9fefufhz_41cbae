"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Food Delivery App Schemas
# --------------------------------------------------

class Restaurant(BaseModel):
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Cuisine type")
    rating: float = Field(4.5, ge=0, le=5, description="Average rating")
    delivery_time_min: int = Field(20, ge=5, le=120, description="Estimated delivery time in minutes")
    image_url: Optional[str] = Field(None, description="Cover image URL")
    is_featured: bool = Field(False, description="Visible in featured section")

class MenuItem(BaseModel):
    restaurant_id: str = Field(..., description="ID of the restaurant this item belongs to")
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    price: float = Field(..., ge=0, description="Price")
    image_url: Optional[str] = Field(None, description="Image URL")
    tags: List[str] = Field(default_factory=list, description="Tags like spicy, vegan")

class OrderItem(BaseModel):
    item_id: str = Field(..., description="Menu item id")
    name: str
    price: float
    quantity: int = Field(1, ge=1)

class Order(BaseModel):
    restaurant_id: str
    restaurant_name: str
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    total: float
    customer_name: str
    address: str
    phone: str
    notes: Optional[str] = None
    status: str = Field("placed", description="placed, preparing, on_the_way, delivered")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
