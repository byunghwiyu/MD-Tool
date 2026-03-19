from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import STATIC_DIR, OUTPUTS_DIR
from app.routes import health, export, jobs, convert

app = FastAPI(title="Local Toolkit")

app.include_router(health.router)
app.include_router(export.router)
app.include_router(jobs.router)
app.include_router(convert.router)

app.mount("/static",  StaticFiles(directory=str(STATIC_DIR)),  name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
