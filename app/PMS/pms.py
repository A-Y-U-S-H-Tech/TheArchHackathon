from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.server import dms

router = APIRouter()

@router.post("/PMS/Create")
async def PMS_Create(request:Request):
    _data = await request.json()
    _flag = dms.Create_Product(_data["PNM"],_data["PCAT"],_data["PDES"],_data["PSTA"])
    if _flag:
        return JSONResponse("ok",200)
    else:
        return JSONResponse("falied",300)
    
@router.post("/PMS/{PID}/Delete")
async def PMS_Delete(PID:int):
    pass

@router.post("/PMS/{PID}/Update")
async def PMS_Update(PID:int):
    pass

@router.get("/PMS/Get_ALL")
def PMS_GetALL():
    pass