from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1")


class Response(BaseModel):
    """
    Response model
    """

    message: str


@router.get("/echo")
async def read_echo():
    return Response(message="Hello World")
