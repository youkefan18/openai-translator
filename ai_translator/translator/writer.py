import sys
import time
from pathlib import Path
from typing import Optional

from datamodel import Book, ContentType
from reportlab.lib import colors, pagesizes, units
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import LOG


class Writer:
    def __init__(self):
        pass

    def save_translated_book(self, book: Book, ouput_file_format: str, output_file_prefix: Optional[str] = None):
        LOG.debug(ouput_file_format)

        if ouput_file_format.lower() == "pdf":
            result_path = self._save_translated_book_pdf(book, output_file_prefix)
        elif ouput_file_format.lower() == "markdown":
            result_path = self._save_translated_book_markdown(book, output_file_prefix)
        else:
            LOG.error(f"不支持文件类型: {ouput_file_format}")
            return ""

        LOG.info(f"翻译完成，文件保存至: {result_path}")

        return result_path


    def _save_translated_book_pdf(self, book: Book, output_file_prefix: Optional[str] = None):
        import time
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        #path = app.config['FILESTORE']['URL'] #[IMPORTANT] Sending quart config will cause serialze problem
        path = './'
        output_file_path=  f'{path}/translated_{timestamp}.pdf' if output_file_prefix is None else f"{output_file_prefix}.pdf"

        LOG.info(f"开始导出: {output_file_path}")

        # Register Chinese font
        font_path = "../fonts/simsun.ttc"  # 请将此路径替换为您的字体文件路径
        pdfmetrics.registerFont(TTFont("SimSun", font_path))

        # Create a new ParagraphStyle with the SimSun font
        simsun_style = ParagraphStyle('SimSun', fontName='SimSun', fontSize=12, leading=14)

        # Create a PDF document
        doc = SimpleDocTemplate(output_file_path, pagesize=pagesizes.letter)
        styles = getSampleStyleSheet()
        story = []

        # Iterate over the pages and contents
        for page in book.pages:
            for content in page.contents:
                if content.status:
                    if content.content_type == ContentType.TEXT:
                        # Add translated text to the PDF
                        text = content.translation
                        para = Paragraph(text, simsun_style)
                        story.append(para)

                    elif content.content_type == ContentType.TABLE:
                        # Add table to the PDF
                        table = content.translation
                        table_style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        pdf_table = Table(table.values.tolist())
                        pdf_table.setStyle(table_style)
                        story.append(pdf_table)
            # Add a page break after each page except the last one
            if page != book.pages[-1]:
                story.append(PageBreak())

        # Save the translated book as a new PDF file
        doc.build(story)
        return output_file_path


    def _save_translated_book_markdown(self, book: Book, output_file_prefix: Optional[str] = None):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        #path = app.config['FILESTORE']['URL'] #[IMPORTANT] Sending quart config will cause serialze problem
        path = './'
        output_file_path=  f'{path}/translated_{timestamp}.md' if output_file_prefix is None else f"{output_file_prefix}.md"

        LOG.info(f"开始导出: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            # Iterate over the pages and contents
            for page in book.pages:
                for content in page.contents:
                    if content.status:
                        if content.content_type == ContentType.TEXT:
                            # Add translated text to the Markdown file
                            text = content.translation
                            output_file.write(text + '\n\n')

                        elif content.content_type == ContentType.TABLE:
                            # Add table to the Markdown file
                            table = content.translation
                            header = '| ' + ' | '.join(str(column) for column in table.columns) + ' |' + '\n'
                            separator = '| ' + ' | '.join(['---'] * len(table.columns)) + ' |' + '\n'
                            # body = '\n'.join(['| ' + ' | '.join(row) + ' |' for row in table.values.tolist()]) + '\n\n'
                            body = '\n'.join(['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in table.values.tolist()]) + '\n\n'
                            output_file.write(header + separator + body)

                # Add a page break (horizontal rule) after each page except the last one
                if page != book.pages[-1]:
                    output_file.write('---\n\n')

        return output_file_path