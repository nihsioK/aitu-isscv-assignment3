from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()
STATIC_DIR = Path(__file__).resolve().parents[2] / "static"


@router.get("/", response_class=FileResponse, include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
