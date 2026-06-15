from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.server import dms
router = APIRouter()

@router.post("/CMS/Create")
async def CMS_Create(request:Request):
    _data:dict = await request.json()
    _flag = dms.Create_Complaint(_data["CUS"],_data["PID"],_data["CDES"],_data["CST"],_data["CSEV"],_data["CDT"])
    if _flag:
        return JSONResponse("ok",200)
    return JSONResponse("falied",400)

@router.post("/CMS/return_all")
async  def CMS_Return_All(request:Request):
    _data = await request.json()
    _flag = dms.Get_Complaints(_data["i"],_data["j"])
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse("falied",400)

@router.get("/CMS/{Complaint_ID}")
def CMS_Return(Complaint_ID:str):
    _flag = dms.Get_Complaint(Complaint_ID)
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse("falied",400)

@router.post("/CMS/{Complaint_ID}/Update")
async def CMS_Update(Complaint_ID:str,request:Request):
    _data = await request.json()
    _flag = dms.Update_Complaint(Complaint_ID,_data["CUS"],_data["PID"],_data["CDES"],_data["CST"],_data["CSEV"],_data["CDT"])
    if _flag:
        return JSONResponse("ok",200)
    else:
        return JSONResponse("falied",400)
    