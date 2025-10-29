from fastapi import FastAPI
from .mongo import col

app = FastAPI()



@app.post("/add_data")
async def add_data():
    
    data = {
        "name": "Naveen Kumar M",
        "college": "Karpagam College of Engineering",
        "department": "CSE",
        "year": 4,
        "skills": ["Python", "FastAPI", "MongoDB", "Spring Boot"]
    }

   
    result = await col.insert_many([data,data])
    return {"id": result}

@app.get("/get_data")
async def get_data():
    cursor = col.find({})
    data = []
    async for document in cursor:
        
        print(type(document['_id']))
        document["_id"] = str(document["_id"]) 
        data.append(document)
    return {"data": data}