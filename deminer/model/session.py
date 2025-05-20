from deminer import db
from .i_dto import IDto
from datetime import datetime

class Session(db.Model, IDto):
    __tablename__ = "sessions"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date: datetime = db.Column(db.DateTime, nullable=False)


    commands = db.relationship('Commands', back_populates='session')
