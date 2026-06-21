from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dms_instance import dms

router = APIRouter()

@router.get("/DAS/overview")
def DAS_overview():
    _data = dms.Get_DasOverview()
    # print(_data)
    return JSONResponse(_data,200)