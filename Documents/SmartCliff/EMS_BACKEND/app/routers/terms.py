from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from bson import ObjectId
from app.database.connection_mongo import content

router = APIRouter(prefix="/TNC",tags=["TNC"])

# ✅ Helper to convert MongoDB ObjectId to string
def content_serializer(content_doc):
    return {
        "id": str(content_doc["_id"]),
        "for_organizers": content_doc.get("for_organizers"),
        "for_audience": content_doc.get("for_audience"),
        "general_terms": content_doc.get("general_terms"),
    }

# ✅ Schema
class ContentSchema(BaseModel):
    for_organizers: List[str]
    for_audience: List[str]
    general_terms: List[str]

class UpdateContentSchema(BaseModel):
    for_organizers: Optional[List[str]] = None
    for_audience: Optional[List[str]] = None
    general_terms: Optional[List[str]] = None


# ✅ Create (Insert)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_content(data: ContentSchema):
    result = await content.insert_one(data.dict())
    new_data = await content.find_one({"_id": result.inserted_id})
    return {"message": "Content added successfully", "data": content_serializer(new_data)}


# ✅ Read (Get All)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_content():
    # Fetch only documents where all 3 fields are not null
    valid_docs = await content.find({
        "for_organizers": {"$ne": None},
        "for_audience": {"$ne": None},
        "general_terms": {"$ne": None}
    }).to_list(100)

    return [content_serializer(c) for c in valid_docs]

# ✅ Read (Get by ID)
@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_content_by_id(id: str):
    data = await content.find_one({"_id": ObjectId(id)})
    if not data:
        raise HTTPException(status_code=404, detail="Content not found")
    return content_serializer(data)


# ✅ Update (by ID)
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_content(id: str, data: UpdateContentSchema):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    result = await content.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No content updated or not found")
    updated_doc = await content.find_one({"_id": ObjectId(id)})
    return {"message": "Content updated successfully", "data": content_serializer(updated_doc)}


# ✅ Delete
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_content(id: str):
    result = await content.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted successfully"}
