from typing import List
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from api import router
from core.config import config
from core.exceptions import CustomException
from core.fastapi.middlewares import (
    AuthenticationMiddleware,
    AuthBackend,
    SQLAlchemyMiddleware,
)
from core.db import engines, Base
from core.utils.logger import debugger


def init_routers(app: FastAPI) -> None:
    app.include_router(router)


def init_listeners(app: FastAPI) -> None:
    # Exception handler
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        # traceback.print_exc()
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        # traceback.print_exc()
        first_error = exc.errors()[0]
        error_message = first_error["msg"]
        _, error_field = first_error["loc"]

        if error_field == "__root__":
            error_field = ""

        return JSONResponse(
            status_code=422,
            content={"error_code": 422, "message": f"{error_field}: {error_message}"}
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware)
    ]
    return middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ably",
        description="Ably",
        version="0.1",
        docs_url=None if config.ENV == "prod" else "/docs",
        redoc_url=None if config.ENV == "prod" else "/redoc",
        middleware=make_middleware()
    )
    init_routers(app=app)
    init_listeners(app=app)
    return app


app = create_app()


async def create_db_tables():
    async with engines["writer"].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('startup')
async def startup():
    debugger.info('Server starting up...')

    await create_db_tables()
    debugger.info('Created default tables')


@app.on_event('shutdown')
async def shutdown_event():
    debugger.info('Server shutting down...')
