from fastapi import FastAPI
from AUTH import auth
from CMS import cms
from TGS import tgs
from PMS import pms
from PKMS import pkms
from dms_instance import dms
from RRS import rrs
from CTAS import ctas
from URSS import urss
import uvicorn
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os



app = FastAPI()

origins = [
    "http://localhost:3000",      # React default port
    "http://localhost:5173",      # Vite / Vue default port
    "https://yourfrontend.com",   # Production domain
]

# 2. Add the CORS middleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allowed domains
    allow_credentials=True,          # Allow cookies and auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all request headers
)



@app.middleware("http")
async def auth_middleware(request, call_next):
        return await auth.Auth_MiddleWare(request, call_next)
# @app.get("/")
# def roo():
#       return FileResponse("app/HTML/fmcg_test_console.html")


dms.Create_User("ayush","08110700","123@gmail.com","SUP")

app.include_router(auth.router)
app.include_router(cms.router)
app.include_router(tgs.router)
app.include_router(pms.router)
app.include_router(pkms.router)
app.include_router(rrs.router)
app.include_router(ctas.router)
app.include_router(urss.router)

if(__name__ == "__main__"):
    uvicorn.run("server:app",host="0.0.0.0",reload=True,port=int(os.environ.get("PORT")))#type:ignore
    