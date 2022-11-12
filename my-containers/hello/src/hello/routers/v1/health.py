from enum import Enum

from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter(prefix="/v1")


class HealthStatus(str, Enum):
    Pass = "pass"  # healthy
    Fail = "fail"  # unhealthy
    Warn = "warn"  # healthy, with some concerns


class HealthResponse(BaseModel):
    """
    Health response model
    https://tools.ietf.org/id/draft-inadarei-api-health-check-01.html#api-health-response
    """

    status: HealthStatus


@router.get("/livez", response_model=HealthResponse)
@router.get("/readyz", response_model=HealthResponse)
def read_health(response: Response):
    response.headers["Content-Type"] = "application/health+json"
    return HealthResponse(
        status=HealthStatus.Pass,
    )
