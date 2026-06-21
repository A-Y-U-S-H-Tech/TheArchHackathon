from fastapi import APIRouter
from dms_instance import dms
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from  datetime import datetime
router = APIRouter()



@router.post("/TGS/create_ticket")
async def TGS_CreateTicket(request:Request):
    _data = await request.json()
    _flag = dms.Create_Ticket(_data["CID"],_data["DEP"],_data["PRI"],False,datetime.now().timestamp(),_data["DES"],_data["ITO"])
    if _flag:
        return JSONResponse("ok",200)
    else:
        return JSONResponse("wrong CID",300)
@router.post("/TGS/return_all")
async def TGS_ReturnAll(request:Request):
    _data = await request.json()  
    _flag = dms.Get_Tickets(_data["i"],_data["j"])
    if _flag :
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse([],400)
    
@router.get("/TGS/{Ticket_ID}/return")
def TGS_Return(Ticket_ID:int):
    _flag = dms.Get_Ticket(Ticket_ID)
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse(" ",400)

@router.post("/TGS/{Ticket_ID}/Update")
async def TGS_Update(request:Request,Ticket_ID:int):
    _data = await request.json()
    dms.Update_Ticket(Ticket_ID,False,False,_data["STA"],_data["PRI"],False,_data["DES"])
    return JSONResponse("ok",200)

@router.post("/TGS/{Ticket_ID}/Escalate")
def TGS_Escalate(request:Request,Ticket_ID:int):
    JSONResponse("ok",200)

@router.post("/TGS/{Ticket_ID}/close")
def TGS_Close(request:Request,Ticket_ID:int):
    dms.Update_Ticket(Ticket_ID,False,False,False,"Resolved",False,False)
    return JSONResponse("ok",200)