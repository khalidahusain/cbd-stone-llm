import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_inference_service, get_validation_service
from backend.app.services.inference import InferenceService
from backend.app.services.validation import ValidationService
from backend.app.schemas.prediction import InsufficientInfoResult

router = APIRouter()


@router.post("/predict")
async def predict(
    features: dict,
    inference_service: InferenceService = Depends(get_inference_service),
    validation_service: ValidationService = Depends(get_validation_service),
):
    # Step 1: Validate input ranges
    validation_errors = validation_service.validate(features)
    if validation_errors:
        return JSONResponse(
            status_code=422,
            content={"errors": [e.model_dump() for e in validation_errors]},
        )

    # Step 2: Run prediction in executor to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, inference_service.predict, features
    )

    # Step 3: Return appropriate response
    if isinstance(result, InsufficientInfoResult):
        return JSONResponse(
            status_code=400,
            content=result.model_dump(),
        )

    return result
