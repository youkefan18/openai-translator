import os
import sqlite3
import sys
from sys import exception
from typing import List, Optional

#append parent path for easier testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Settings
from datamodel.history import History
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import LOG


class SqliteDb:
    __dbpath = "./translations.db"
    engine = None

    def __init__(self, config: Optional[Settings] = None):
        if config is not None:
            self.__dbpath = config.DATABASE_URL
        self._initdb()
        self.engine = create_engine(f'sqlite:///{self.__dbpath}')

    def _initdb(self):
        conn = sqlite3.connect(self.__dbpath)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT , 
                    username TEXT default "anonymous" NOT NULL, 
                    source_file_name TEXT, 
                    source_file_path TEXT,
                    target_file_name TEXT,
                    target_file_path TEXT,
                    target_language TEXT default "chinese" NOT NULL,
                    process_time datetime default (datetime('now','localtime')),
                    pages INT,
                    status TEXT default "PROCESSING" NOT NULL)"""
            )
            cursor.execute("""
                insert OR REPLACE into translations  
                    (id, source_file_name, source_file_path, target_file_name, target_file_path, pages, status)
                    values (1, 'test.pdf', '../tests/test.pdf', 'test_translated.md', '../tests/test_translated.md', 1, 'DONE')
            """)
            conn.commit()
        except exception as e:
            LOG.error(e)
        finally:
            cursor.close
            conn.close

    def query_history(self) -> List[History]:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        history = session.query(History).all()
        LOG.info(history[0])
        session.close()
        return history

if __name__ == "__main__":
    print()
    print(SqliteDb(Settings()).query_history()[0].source_file_name)