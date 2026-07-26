from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.common.exceptions import ApplicationException
from shared.common.schemas import DefaultResponse

def init_exception_handlers(app: FastAPI):
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        return JSONResponse(
            status_code=exc.code,
            content=DefaultResponse.error(
                message=exc.message,
                code=exc.code
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content=DefaultResponse.error(
                message="Validation Error",
                code=400,
                data=exc.errors()
            ).model_dump()
        )

    @app.exception_handler(ValueError)
    @app.exception_handler(TypeError)
    async def common_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=400,
            content=DefaultResponse.error(
                message=str(exc),
                code=400
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=DefaultResponse.error(
                message="Internal Server Error",
                code=500
            ).model_dump()
        )
