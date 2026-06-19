from fastapi import APIRouter,File,Form,UploadFile
from fastapi.responses import JSONResponse
from dms_instance import dms
import json
from RRS import rrs
from json import JSONDecodeError
router = APIRouter()


@router.post("/PKMS/upload_document")
async def PKMS_UploadDocument(Ufile:UploadFile,metaData:str = Form()):
    print(metaData)
    _data = {}
    if(metaData == None):
        return JSONResponse("invalid Metadata",400)
    else:
        try:
            _data = json.loads(metaData)
        except JSONDecodeError as e:
            return JSONResponse("Wrong Metadata",400)
    file_path = ""+_data["DTYPE"]+Ufile.filename #type:ignore
    dms.Create_KDocument(_data["DNM"],_data["DTYPE"],file_path)
    _file = await Ufile.read()
    _flag = dms.upload_file_to_supabase(_file,"TheArchHacathon",file_path)#type:ignore
    _DTYPE = _data["DTYPE"].split("/")
    rrs.ingest_pdfFile_to_VectorDB(_file,_data["DNM"],_DTYPE[0],_DTYPE[1],"RAG")
    if(_flag == None):
        return JSONResponse("falied",400)
    else:
        return JSONResponse("ok",200)

@router.post("PKMS/all_documents")
async def PKMS_getALL():
    pass

@router.post("PKMS/{Document_ID}/Delete")
async def PKMS_Delete():
    pass