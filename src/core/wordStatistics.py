from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mawo_pymorphy3


class WordStatistics:
    def __init__(self):
        self.morph = mawo_pymorphy3.MorphAnalyzer()
        self.stats = defaultdict(lambda: {
            'total': 0,
            'by_line': []
        })
        self.current_line_counts = defaultdict(int)
        self.line_num = 0
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def process_word(self, word: str):
        loop = asyncio.get_event_loop()
        parsed = await loop.run_in_executor(
            self.executor,
            lambda: self.morph.parse(word)[0]
        )
        normal_form = parsed.normal_form

        self.current_line_counts[normal_form] += 1
        self.stats[normal_form]['total'] += 1

    async def end_of_line(self):
        for word, count in self.current_line_counts.items():
            if len(self.stats[word]['by_line']) < self.line_num:
                self.stats[word]['by_line'].extend(
                    [0] * (self.line_num - len(self.stats[word]['by_line']))
                )
            self.stats[word]['by_line'].append(count)

        for word, data in self.stats.items():
            if word not in self.current_line_counts:
                if len(data['by_line']) <= self.line_num:
                    data['by_line'].append(0)

        self.current_line_counts.clear()
        self.line_num += 1

    def get_statistics(self):
        return self.stats