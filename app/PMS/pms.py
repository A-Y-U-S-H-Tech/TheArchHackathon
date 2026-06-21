from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from dms_instance import dms

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
    _flag = dms.Delete_Product(PID)
    if _flag :
        return JSONResponse("ok",200)
    else:
        return JSONResponse("falied",400)

@router.post("/PMS/{PID}/Update")
async def PMS_Update(PID:int):
    pass

@router.post("/PMS/Get_ALL")
async def PMS_GetALL(request:Request):
    _data = await request.json()
    _flag = dms.Get_Products(_data["i"],_data["j"])
    if _flag:
        return JSONResponse(_flag[1])
    else:
        return JSONResponse(" ",400)
    
@router.get("/PMS/{Product_ID}/Get")
def PMS_Get(Product_ID:int):
    _flag = dms.Get_Product(Product_ID)
    if _flag:
        return JSONResponse(_flag[1])
    else:
        return JSONResponse(" ",400)