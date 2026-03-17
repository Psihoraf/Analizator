from fastapi import UploadFile, BackgroundTasks
from starlette.responses import FileResponse

from src.services.fileReader import FileReader
from src.services.excelExporter import ExcelExporter
from src.core.wordStatistics import WordStatistics


class WordStatisticsProcessor:
    def __init__(self):
        self.reader = FileReader()
        self.statistics = WordStatistics()
        self.exporter = ExcelExporter()

    async def process_file(self, file: UploadFile, background_tasks: BackgroundTasks) -> FileResponse:
        await self.reader.read_words(
            file,
            word_handler=self._word_callback,
            line_end_handler=self._line_end_callback
        )

        stats = self.statistics.get_statistics()
        return await self.exporter.export(stats, background_tasks)

    async def _word_callback(self, word: str):
        await self.statistics.process_word(word)

    async def _line_end_callback(self):
        await self.statistics.end_of_line()