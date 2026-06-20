from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from dms_instance import dms

router = APIRouter()

@router.post("/URSS/Complain/return_all")
async def URSS_returnAll(request:Request):
    _data = await request.json()
    _flag = dms.Get_UserComplains(request.state.UNAM,_data["i"],_data["j"])
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse("falied",400)

@router.get("/URSS/Complain/latest")
def URSS_returnLatest(request:Request):
    _flag = dms.Get_UserComplainLatest(request.state.UNAM)
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse("falied",400)

@router.get("/URSS/Complain_Progress/{Complain_ID}")
def URSS_ComplainUpdate(Complain_ID:int,request:Request):
    _flag = dms.Get_UserTickets(request.state.UNAM,Complain_ID)
    if _flag:
        return JSONResponse(_flag[1],200)
    else:
        return JSONResponse("falied",400)