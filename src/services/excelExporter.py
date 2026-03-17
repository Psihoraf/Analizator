import os
import tempfile
import asyncio
import pandas as pd
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any
from openpyxl.styles import Font, PatternFill


class ExcelExporter:
    @staticmethod
    async def export(stats: Dict[str, Any], background_tasks: BackgroundTasks) -> FileResponse:
        loop = asyncio.get_event_loop()

        data = await loop.run_in_executor(
            None,
            lambda: ExcelExporter._prepare_data(stats)
        )

        df = await loop.run_in_executor(
            None,
            lambda: pd.DataFrame(data).sort_values('всего', ascending=False)
        )

        tmp_path = await loop.run_in_executor(
            None,
            lambda: ExcelExporter._create_excel_file(df)
        )

        background_tasks.add_task(ExcelExporter._cleanup_temp_file, tmp_path)

        return FileResponse(
            path=tmp_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='word_statistics.xlsx'
        )

    @staticmethod
    def _prepare_data(stats):
        data = []
        for normal_form, info in stats.items():
            if normal_form:
                line_counts_str = ','.join([str(count) for count in info['by_line']])
                data.append({
                    'слово': normal_form,
                    'всего': info['total'],
                    'по строкам': line_counts_str
                })
        return data

    @staticmethod
    def _create_excel_file(df):
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        tmp_path = tmp_file.name
        tmp_file.close()

        with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Статистика', index=False)

            worksheet = writer.sheets['Статистика']

            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font

        return tmp_path

    @staticmethod
    def _cleanup_temp_file(path: str):
        if os.path.exists(path):
            os.unlink(path)