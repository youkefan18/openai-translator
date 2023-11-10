import dataclasses
import os
import time
from dataclasses import dataclass
from typing import List, Literal, Optional

import ray
from attr import field
from backend_db import SqliteDb
from fastapi import Depends, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils import LOG

from ai_translator.translator.pdf_translator import PDFTranslator
from config import get_settings

#Init Quart App
app = FastAPI()
origins = [
    "https://chat.openai.com",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#TODO get env from os
config = get_settings()

#Init Ray
ray.init(num_cpus=2, local_mode=(config.ENVIRONMENT=='dev'))

## Set up database
db = SqliteDb(config)

#Swagger UI: localhost:5000/docs or localhost:5000/redocs 

@dataclass
class QueryTranslate:
    language: Literal["Chinese", "Italian"]
    model: Literal["api2d-gpt-3.5-turbo", "openai-gpt-3.5-turbo", "chatglm-gpt-3.5-turbo"]
    file_ext: Literal["PDF", "markdown"]
    page_num: int = 1
    filename: Optional[str] = None

    def __reduce__(self):
        #t = (self.language,self.model,self.file_ext,self.page_num,self.filename)
        t = tuple(dataclasses.asdict(self).values())
        return QueryTranslate, t

@app.get("/ping")
async def ping():
    """Test connection

    Returns:
        _type_: content-type: text/html; charset=utf-8
    """
    return "pong"

@app.get("/history")
async def translation_history():
    """Get list of translation histories

    Returns:
        _type_: content-type: applicaiton/json; charset=utf-8
    """
    #print(request.is_json, request.mimetype)
    histories = db.query_history()
    LOG.info(histories)
    return histories

@app.post("/translate")
async def translation(files: List[UploadFile], data: QueryTranslate = Depends()):
    result = {}
    for file in files: 
        data.filename = file.filename
        LOG.info(f'Translating {data.page_num} pages of {data} to language {data.language} using mdoel {data.model}')
        content = await file.read()
        result[file.filename] = translate.remote(file=content, param=data) # type: ignore
    output = ray.get(list(result.values()))
    return output

@ray.remote
def translate(file, param: QueryTranslate):
    #(file, param) = ray.get(refs)
    print(f'file: {file}, param: {param}')
    #datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    #path = app.config['FILESTORE']['URL'] #[IMPORTANT] Sending quart config will cause serialze problem
    path = './'
    outfilename = f'{path}/translated_{timestamp}.{param.file_ext}'

    translator = PDFTranslator(param.model)
    translated = translator.translate_pdf(
        input_file=file, 
        output_file_format=param.file_ext,
        target_language=param.language,
        pages=param.page_num
    )

    # with open(outfilename, 'wb') as output_file:
    #     output_file.write(file)
    print(f'Translated file! {outfilename}')
    return os.path.abspath(outfilename)

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run()