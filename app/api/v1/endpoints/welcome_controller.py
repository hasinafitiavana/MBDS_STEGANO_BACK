

from fastapi import APIRouter, HTTPException
router = APIRouter()
@router.post("/")
async def welcome():
    try:
        return {"message": "Welcome to the API!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))