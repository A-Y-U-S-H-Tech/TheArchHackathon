from fastapi import FastAPI
from AUTH import auth
from CMS import cms
from TGS import tgs
from PMS import pms
from PKMS import pkms
from dms_instance import dms
from RRS import rrs
from CTAS import ctas
import uvicorn
from fastapi.responses import FileResponse



app = FastAPI()

@app.middleware("http")
async def auth_middleware(request, call_next):
        return await auth.Auth_MiddleWare(request, call_next)
@app.get("/")
def roo():
      return FileResponse("app/HTML/fmcg_test_console.html")


dms.Create_User("ayush","08110700","123@gmail.com","SUP")

app.include_router(auth.router)
app.include_router(cms.router)
app.include_router(tgs.router)
app.include_router(pms.router)
app.include_router(pkms.router)
app.include_router(rrs.router)
app.include_router(ctas.router)

if(__name__ == "__main__"):
    uvicorn.run("server:app",host="localhost",reload=True,port=8080)
    