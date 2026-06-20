from dms_instance import dms
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import jwt
from uuid import uuid4
from datetime import datetime,timezone,timedelta

router = APIRouter()

Scerete_Key = str(uuid4)
def GenJWT(NAM:str,ROL:str)->str:
    payload = {
        "NAM":NAM,
        "ROL":ROL,
        "exp":datetime.now(timezone.utc)+timedelta(hours=1),
    }
    print(payload)
    return jwt.encode(payload,Scerete_Key,"HS256")
def JWT_Validate(jwt:dict)->bool:
    if int((datetime.now(timezone.utc)-timedelta(hours=1)).timestamp()) <= jwt["exp"]:
        return True
    return False



ALLOWED_PATH = "/AMS/login","/AMS/signup","/"

async def Auth_MiddleWare(request:Request,call_next):
    _path = request.url.path
    if _path in ALLOWED_PATH:
        return await call_next(request)
    else:
        if request.method == "OPTIONS":
           return await call_next(request)
        if "JWT" in request.cookies.keys():
            _decode =''
            try :
                _decode = jwt.decode(request.cookies.get("JWT"),Scerete_Key,"HS256")#type:ignore
            except:
                return JSONResponse("Not auth",401)
            if dms.Check_User(_decode["NAM"]) and JWT_Validate(_decode):
                request.state.UNAM = _decode["NAM"]
                request.state.UROL = _decode["ROL"]
                return await call_next(request)
            else:
                return JSONResponse("Invalid",401)
        else:
            return JSONResponse("Not Auth",401)
    
@router.post("/AMS/login")
async def auth_login(request:Request):
    _cred = await request.json()
    if(dms.Check_Validate_User(_cred["NAM"],_cred["PAS"])):
        response = JSONResponse("ok",200)
        _jwt = GenJWT(_cred["NAM"],dms.Get_User_role(_cred["NAM"]))#type:ignore
        response.set_cookie(
            "JWT",
            _jwt,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return response
    else:
        return JSONResponse("Not Valid",401)

@router.post("/AMS/signup")
async def auth_signup(request:Request):
    _cred = await request.json()
    if _cred["ROL"]  == "CSE":
        if "session" in request.cookies.keys():
            _jwt = jwt.decode(request.cookies.get("JWT"),Scerete_Key,"HS256") #type:ignore
            if _jwt["ROL"] != "SUP":
                return JSONResponse("Not Auth",401)
    if _cred["ROL"] == "SUP":
        return JSONResponse("Not valid",400)
    _flag = dms.Create_User(_cred["NAM"],_cred["PAS"],_cred["EMA"],_cred["ROL"])
    if(_flag):
        return JSONResponse("ok",200)
    else:
        return JSONResponse("Already Exits",400)

@router.post("/AMS/logout")
def auth_logout():
    return JSONResponse("ok",200)
