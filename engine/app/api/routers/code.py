import uuid
import logging
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from app.llm.modules.code import CodeGenerationModule
from app.utils import APP_LOGGER_NAME

router = APIRouter()

logger = logging.getLogger(APP_LOGGER_NAME).getChild(__name__)

class CodeGenerationReq(BaseModel):
    query: str

    model_config = {
        "from_attributes": True,
    }

class CodeGenerationResp(BaseModel):
    code: str

    model_config = {
        "from_attributes": True,
    }

@router.post(
    "/generate",
    response_model=CodeGenerationResp,
    status_code=status.HTTP_200_OK,
    summary="Check the health of the API",
)
async def health_check(req: CodeGenerationReq):
    """
    Health check endpoint.
    """
    try:
        session_id = uuid.uuid4()
        code_module = CodeGenerationModule(
            session_id=session_id,
        )

        output = await code_module.aforward(
            "",
            req.query
        )

        if not output or not hasattr(output, 'code'):
            logger.error("Generated code is empty or does not have 'code' attribute.")
            raise ValueError("Generated code is empty or invalid.")


        generated_code = output.code

        if not generated_code and isinstance(generated_code, str):
            logger.error("Generated code is empty or invalid.")
            raise ValueError("Generated code is empty or invalid.")

        return CodeGenerationResp(
            code=generated_code,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )