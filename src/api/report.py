from fastapi import APIRouter, BackgroundTasks
from fastapi import UploadFile
from src.exceptions.exceptions import check_file_extension
from src.core.wordStatisticsProcessor import WordStatisticsProcessor
router = APIRouter(prefix="/report",tags= ["Отчет"])

@router.post("",  response_model=None)
async def report(file: UploadFile, background_tasks: BackgroundTasks):

    check_file_extension(file.filename)
    processor = WordStatisticsProcessor()
    return await processor.process_file(file, background_tasks)



