import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))
from chains import TranslationChain
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG


class PDFTranslator:
    def __init__(self, model: str):
        self.translate_chain = TranslationChain(model)
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self,
                    input_file: str,
                    output_file_format: str = 'markdown',
                    source_language: str = "English",
                    target_language: str = 'Chinese',
                    pages: Optional[int] = None):
        
        self.book = self.pdf_parser.parse_pdf(input_file, pages)

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                # Translate content.original
                translation, status = self.translate_chain.run(content, source_language, target_language)
                # Update the content in self.book.pages directly
                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)
        
        return self.writer.save_translated_book(self.book, output_file_format)
    
if __name__ == "__main__":
    translator = PDFTranslator("api2d-gpt-3.5-turbo")
    translated = translator.translate_pdf(
        input_file="tests/test.pdf", 
        output_file_format="pdf",
        target_language="Chinese",
        pages=1
    )
    print(translated)