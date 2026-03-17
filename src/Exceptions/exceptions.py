from pathlib import Path

from fastapi import HTTPException


def check_file_extension(filename: str):
    allowed_extensions = {'.txt', '.csv', '.md', '.py', '.html', '.xml', '.json', '.docx'}
    file_extension = Path(filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise FileExtensionExceptions


class AnalizatorExceptions(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class FileExtensionExceptions(AnalizatorExceptions):
    detail = "Неверное расширение"

class EncodingExceptions(AnalizatorExceptions):
    detail = "Не удалось определить кодировку файла или кодировка не поддерживается"

class AnalizatorHTTPExceptions(HTTPException):
    status_code = 404
    detail = None
    def __init__(self, detail: str = None, *args, **kwargs):
        detail = detail or self.detail
        super().__init__(status_code=self.status_code, detail=detail)

class FileExtensionHTTPExceptions(AnalizatorHTTPExceptions):
    status_code = 400
    detail = "Неверное расширение файла"

class EncodingHTTPExceptions(AnalizatorHTTPExceptions):
    status_code = 400
    detail = "Не удалось определить кодировку файла. Поддерживаются только файлы с явно определяемой кодировкой"