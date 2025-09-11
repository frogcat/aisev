from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    print("/hello endpoint accessed")
    return {"message": "hello"}
