from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dms_instance import dms

router = APIRouter()

@router.get("/STAT")
def STAT():
    _data = dms.GET_STAT()
    JSONResponse(_data,200)