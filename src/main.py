from fastapi import FastAPI, Request
from src.api.report import router as report_router
from src.exceptions.exceptions import EncodingExceptions, EncodingHTTPExceptions, FileExtensionExceptions, \
    FileExtensionHTTPExceptions


app = FastAPI()

# Глобальные обработчики исключений
@app.exception_handler(EncodingExceptions)
async def encoding_exception_handler(request: Request, exc: EncodingExceptions):

    raise EncodingHTTPExceptions

@app.exception_handler(FileExtensionExceptions)
async def file_extension_exception_handler(request: Request, exc: FileExtensionExceptions):

    raise FileExtensionHTTPExceptions



app.include_router(report_router)

@app.get("/docs")
async def root():
    return {"message": "Hello World"}