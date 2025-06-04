from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

items = ['my list, add to it with .append']

class ItemRequest(BaseModel):
    item: str

@app.get("/")
def read_root():
    return {"message": "use the api endpoint /api/data"}

@app.get("/api/data")
def get_data():
    return {"data": items}

@app.post("/api/send_data")
def create_item(data: ItemRequest):
    items.append(data.item)
    return {
        "message": f"Item '{data.item}' added successfully!",
        "added_item": data.item,
        "total_items": len(items),
        "items": items
    }
