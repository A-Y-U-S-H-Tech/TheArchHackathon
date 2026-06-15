from DMS.DMS import DMS
from fastapi import FastAPI
from AUTH import auth
from CMS import cms
from TGS import tgs
from PMS import pms
dms = DMS()

app = FastAPI()

app.include_router(auth.router)
app.include_router(cms.router)
app.include_router(tgs.router)
app.include_router(pms.router)
