from abc import ABC
from typing import List, Dict

from http import HTTPStatus
from flask import abort

from sqlalchemy import inspect
from sqlalchemy.orm import Mapper

from deminer import db

class GeneralController(ABC):
    """
    The common realization of controller.
    """
    _model_type = db.Model
    _session = db.session

    def find_all(self) -> List[object]:
        """
        Gets all objects from table using Service layer as DTO objects.
        :return: list of all objects as DTOs
        """
        obj = self._session.query(self._model_type).all()
        return list(map(lambda x: x.put_into_dto(), obj))

    def find_by_id(self, key: int) -> object:
        """
        Gets object from database table by integer key using from Service layer.
        :param key: integer key (surrogate primary key)
        :return: DTO for search object
        """
        obj = self._session.query(self._model_type).get(key)
        if obj is None:
            abort(HTTPStatus.NOT_FOUND)
        return obj.put_into_dto()

    def create(self, obj: object) -> object:
        """
        Creates object in database table using Service layer.
        :param obj: object to create in Database
        :return: DTO for created object
        """
        self._session.add(obj)
        self._session.commit()
        return obj.put_into_dto()

    def update(self, key: int, new_obj: object) -> None:
        """
        Updates object in database table using Service layer.
        :param key: integer key (surrogate primary key)
        :param new_obj: object to create in Database
        """
        obj = self.find_by_id(key)
        if obj is None:
            abort(HTTPStatus.NOT_FOUND)
        
        domain_obj = self._session.query(self._model_type).get(key)
        mapper: Mapper = inspect(type(new_obj))  # Metadata
        columns = mapper.columns._collection
        for column_name, column_obj, *_ in columns:
            if not column_obj.primary_key:
                value = getattr(new_obj, column_name)
                setattr(domain_obj, column_name, value)
        self._session.commit()

    def patch(self, key: int, value_dict: Dict[str, object]) -> None:
        """
        Modifies defined field of object in database table using Service layer.
        :param key: integer key (surrogate primary key)
        :param value_dict: key-values
        """
        obj = self.find_by_id(key)
        if obj is None:
            abort(HTTPStatus.NOT_FOUND)
        for field_name, value in value_dict.items():
            domain_obj = self._session.query(self._model_type).get(key)
            setattr(domain_obj, field_name, value)
            self._session.commit()

    def delete(self, key: int) -> None:
        """
        Deletes object from database table by integer key from Service layer.
        :param key: integer key (surrogate primary key)
        """
        obj = self.find_by_id(key)
        if obj is None:
            abort(HTTPStatus.NOT_FOUND)

        domain_obj = self._session.query(self._model_type).get(key)
        self._session.delete(domain_obj)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def delete_all(self) -> None:
        """
        Deletes all objects from database table using Service layer.
        """
        self._session.query(self._domain_type).delete()
        self._session.commit()