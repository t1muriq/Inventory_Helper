from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, TypeVar, Generic, Type

# Определяем обобщенный тип для моделей
T = TypeVar('T')


class Repository(Generic[T]):
    """
    Базовый класс репозитория для работы с моделями SQLAlchemy.
    Предоставляет основные CRUD операции.
    
    Generic[T] означает, что класс параметризован типом T,
    который будет определен при создании конкретного репозитория.
    """
    
    def __init__(self, session, model_class: Type[T]):
        """
        Инициализация репозитория.
        
        Args:
            session: Сессия SQLAlchemy для работы с базой данных.
            model_class: Класс модели SQLAlchemy, с которой работает репозиторий.
        """
        self.session = session
        self.model_class = model_class
    
    def get_all(self) -> List[T]:
        """
        Получает все записи модели.
        
        Returns:
            List[T]: Список всех записей.
        """
        return self.session.query(self.model_class).all()
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Получает запись по ID.
        
        Args:
            id: ID записи.
            
        Returns:
            Optional[T]: Запись с указанным ID или None, если запись не найдена.
        """
        return self.session.query(self.model_class).filter(self.model_class.id == id).first()
    
    def create(self, model: T) -> T:
        """
        Создает новую запись в базе данных.
        
        Args:
            model: Экземпляр модели для создания.
            
        Returns:
            T: Созданная запись.
            
        Raises:
            SQLAlchemyError: Если произошла ошибка при создании записи.
        """
        try:
            self.session.add(model)
            self.session.commit()
            return model
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def update(self, model: T) -> T:
        """
        Обновляет существующую запись в базе данных.
        
        Args:
            model: Экземпляр модели для обновления.
            
        Returns:
            T: Обновленная запись.
            
        Raises:
            SQLAlchemyError: Если произошла ошибка при обновлении записи.
        """
        try:
            self.session.merge(model)
            self.session.commit()
            return model
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def delete(self, id: int) -> bool:
        """
        Удаляет запись по ID.
        
        Args:
            id: ID записи для удаления.
            
        Returns:
            bool: True, если запись успешно удалена, иначе False.
            
        Raises:
            SQLAlchemyError: Если произошла ошибка при удалении записи.
        """
        try:
            model = self.get_by_id(id)
            if model:
                self.session.delete(model)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
    
    def delete_all(self) -> bool:
        """
        Удаляет все записи модели.
        
        Returns:
            bool: True, если записи успешно удалены.
            
        Raises:
            SQLAlchemyError: Если произошла ошибка при удалении записей.
        """
        try:
            self.session.query(self.model_class).delete()
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e