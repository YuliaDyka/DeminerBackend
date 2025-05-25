from deminer import db
from .i_dto import IDto
from datetime import datetime

class Session(db.Model, IDto):
    __tablename__ = "sessions"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date: datetime = db.Column(db.DateTime, nullable=False)
    name: str = db.Column(db.String(45), nullable=False)


    commands = db.relationship('Commands', back_populates='session')

    def put_into_dto(self):
        return {
            "id": self.id,
            "date": self.date,
            "name": self.name,
        
            "commands": list(map(lambda a: a.put_into_dto(), self.commands)),
            }