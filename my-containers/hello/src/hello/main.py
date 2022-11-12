import logging
import os

from fastapi import FastAPI

from hello import routers

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=LOG_LEVEL)


app = FastAPI()

app.include_router(
    router=routers.v1.health.router,
    tags=["Health"],
)

app.include_router(
    router=routers.v1.echo.router,
    tags=["Echo"],
)
