import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from routers.generate import router as generate_router

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
for folder in ("uploads", "generated"):
    (BASE_DIR / folder).mkdir(exist_ok=True)

app = FastAPI(title="Resume Tailor API")

allowed_origins = [
    o.strip() for o in os.getenv("CLIENT_ORIGIN", "http://localhost:5173").split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


app.include_router(generate_router, prefix="/api")

# Serve generated PDFs for download, e.g. GET /files/resume-<id>.pdf
app.mount("/files", StaticFiles(directory=str(BASE_DIR / "generated")), name="files")


# Keep the response shape identical to what the frontend expects: {"error": "..."}
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 5000)), reload=True)
