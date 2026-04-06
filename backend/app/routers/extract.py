from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.dependencies import get_extraction_service
from backend.app.services.extraction import ExtractionService, ExtractionError

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str


@router.post("/extract")
async def extract(
    request: ExtractRequest,
    extraction_service: ExtractionService = Depends(get_extraction_service),
):
    if extraction_service is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Extraction service unavailable. OPENAI_API_KEY not configured."},
        )

    try:
        result = await extraction_service.extract(request.text)
        return result
    except ExtractionError as e:
        status = 400 if e.safeguard_triggered else 502
        return JSONResponse(status_code=status, content={"error": str(e)})
