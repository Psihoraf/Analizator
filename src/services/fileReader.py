from fastapi import UploadFile
import asyncio
import chardet

from src.Exceptions.exceptions import EncodingExceptions


class FileReader:
    def __init__(self):
        self.buffer = ""
        self.chunk_size = 64 * 1024
        self.encoding = None
        self.encoding_confidence = 0

    async def read_words(self, file: UploadFile, word_handler, line_end_handler=None):
        loop = asyncio.get_event_loop()

        # Читаем первые байты для определения кодировки
        first_chunk = await file.read(min(10000, self.chunk_size))
        if not first_chunk:
            return

        # Определяем кодировку
        encoding_result = await loop.run_in_executor(
            None,
            lambda: chardet.detect(first_chunk)
        )

        self.encoding = encoding_result['encoding']
        self.encoding_confidence = encoding_result['confidence']

        if self.encoding is None or self.encoding_confidence < 0.7:
            raise EncodingExceptions

        # Обрабатываем первый чанк
        text_chunk = await loop.run_in_executor(
            None,
            lambda: first_chunk.decode(self.encoding, errors='replace')
        )
        await self.process_chunk(text_chunk, word_handler, line_end_handler)

        # Читаем остаток файла
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break

            text_chunk = await loop.run_in_executor(
                None,
                lambda: chunk.decode(self.encoding, errors='replace')
            )
            await self.process_chunk(text_chunk, word_handler, line_end_handler)

        await file.close()
        await self.flush_buffer(word_handler, line_end_handler)

    async def process_chunk(self, chunk: str, word_handler, line_end_handler=None):
        loop = asyncio.get_event_loop()
        lines = await loop.run_in_executor(None, lambda: chunk.split('\n'))

        self.buffer += lines[0] if lines else ""

        for line in lines[1:]:
            await self.process_line(line, word_handler)
            if line_end_handler:
                await line_end_handler()

    async def flush_buffer(self, word_handler, line_end_handler=None):
        if self.buffer.strip():
            await self.process_line(self.buffer, word_handler)
            if line_end_handler:
                await line_end_handler()

    @staticmethod
    def _clean_word(word: str) -> str:
        return word.strip('.,!?;:()[]{}"\'«»—–').lower()

    async def process_line(self, line: str, word_handler):
        loop = asyncio.get_event_loop()
        words = await loop.run_in_executor(None, lambda: line.split())

        for word in words:
            clean_word = self._clean_word(word)
            if clean_word:
                await word_handler(clean_word)