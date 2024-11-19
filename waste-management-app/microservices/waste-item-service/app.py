from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymongo
from bson import ObjectId  # Import để xử lý ObjectId của MongoDB
import os

app = FastAPI()

# Connect to MongoDB Atlas
mongo_url = os.environ.get('MONGO_URL')
database_name = os.environ.get('DATABASE_NAME')

if not mongo_url or not database_name:
    raise ValueError("Environment variables MONGO_URL and DATABASE_NAME must be set")

client = pymongo.MongoClient(mongo_url)
db = client[database_name]

# Định nghĩa mô hình WasteItem
class WasteItem(BaseModel):
    name: str
    category: str
    sorting_instructions: str

@app.post("/waste-items/")
async def create_waste_item(item: WasteItem):
    item_data = item.dict()
    result = db.waste_items.insert_one(item_data)
    return {"message": "Waste item created successfully", "item_id": str(result.inserted_id)}

@app.get("/waste-items/")
async def get_items():
    items = list(db.waste_items.find({}))
    # Chuyển đổi ObjectId sang chuỗi cho mỗi item
    for item in items:
        item["_id"] = str(item["_id"])
    return items

@app.put("/waste-items/{item_id}")
async def update_item(item_id: str, item: WasteItem):
    try:
        object_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = db.waste_items.update_one({"_id": object_id}, {"$set": item.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Waste item not found")
    return {"message": "Waste item updated successfully"}

@app.delete("/waste-items/{item_id}")
async def delete_item(item_id: str):
    try:
        object_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = db.waste_items.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Waste item not found")
    return {"message": "Waste item deleted successfully"}


@app.get("/waste-items/{item_id}")
async def get_item(item_id: str):
    try:
        object_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    item = db.waste_items.find_one({"_id": object_id})
    if not item:
        raise HTTPException(status_code=404, detail="Waste item not found")

    item["_id"] = str(item["_id"])
    return item
