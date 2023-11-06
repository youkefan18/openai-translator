# pyright:  reportGeneralTypeIssues = false

#See lint problem here https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html
#Fix dataclasses.asdict fail to convert to dict: https://segmentfault.com/a/1190000042881840
#https://code.likeagirl.io/using-data-classes-to-create-database-models-in-python-b936301aa4ad
from dataclasses import dataclass
import dataclasses
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

@dataclass
class History(Base):
    __tablename__ ='translations'

    id: int = Column(Integer, primary_key=True, autoincrement="auto")
    username: str = Column(String)
    source_file_name: str = Column(String)
    source_file_path: str = Column(String)
    target_file_name: str = Column(String)
    target_file_path: str  = Column(String)
    target_language: str  = Column(String)
    process_time: datetime = Column(DateTime, default = datetime.now)
    pages: int = Column(Integer, default = 1)
    status: str = Column(String)

    def __reduce__(self):
        t = tuple(dataclasses.asdict(self).values())
        return History, t

if __name__ == "__main__":
    h = History(id = 1, username='anonymous',  
                source_file_name = 'test.pdf', 
                source_file_path='../tests/test.pdf', 
                target_file_name='test_translated.md', 
                target_file_path='../tests/test_translated.md', 
                target_language = 'chinese', pages=1, 
                status='DONE')
    print(h.__reduce__)