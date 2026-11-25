from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.security import require_admin
from app.services.system import trigger_deploy

router = APIRouter(prefix="/system", tags=["system"])


@router.post("/deploy")
def deploy(_: dict = Depends(require_admin)):
    body, status_code = trigger_deploy()
    return JSONResponse(content=body, status_code=status_code)
