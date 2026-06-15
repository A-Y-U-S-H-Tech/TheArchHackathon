from fastapi import APIRouter
from app.server import dms
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from  datetime import datetime
router = APIRouter()



@router.post("/TGS/create_ticket")
async def TGS_CreateTicket(request:Request):
    _data = await request.json()
    _flag = dms.Create_Ticket(_data["CID"],_data["DEP"],_data["PRI"],False,datetime.now().timestamp())
    if _flag:
        return JSONResponse("ok",200)
    else:
        return JSONResponse("wrong CID",300)
    
@router.post("/TGS/{Ticket_ID}/Update")
def TGS_Update(request:Request):
    pass

@router.post("/TGS/{Ticket_ID}/Escalate")
def TGS_Escalate(request:Request):
    pass

@router.post("/TGS/{Ticket_ID}/close")
def TGS_Close(request:Request):
    pass