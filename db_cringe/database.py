from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os

# Базовый класс для моделей
Base = declarative_base()


class Database:
    def __init__(self, db_url=None):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_url (str, optional): URL подключения к базе данных PostgreSQL.
                Если не указан, будет использоваться значение из переменной окружения DATABASE_URL
                или значение по умолчанию для локальной разработки.
        """
        if db_url is None:
            db_url = os.environ.get(
                'DATABASE_URL',
                'postgresql://postgres:postgres@localhost:5432/inventory'
            )
        
        # Создаем движок с явными параметрами подключения
        self.engine = create_engine(
            db_url,
            connect_args={'client_encoding': 'utf8'}
        )
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def create_tables(self):
        """
        Создает все таблицы в базе данных на основе определенных моделей.
        """
        from library.src.application.db.models import Base
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """
        Удаляет все таблицы из базы данных.
        """
        from library.src.application.db.models import Base
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """
        Возвращает новую сессию для работы с базой данных.
        
        Returns:
            Session: Объект сессии SQLAlchemy.
        """
        return self.Session()
    
    def close_session(self, session):
        """
        Закрывает сессию базы данных.
        
        Args:
            session: Сессия SQLAlchemy для закрытия.
        """
        if session:
            session.close()
    
    def close_all_sessions(self):
        """
        Закрывает все сессии базы данных.
        """
        self.Session.remove()