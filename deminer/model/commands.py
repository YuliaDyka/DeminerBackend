from deminer import db
from .i_dto import IDto


class Commands(db.Model, IDto):
    __tablename__ = "commands"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    index: int = db.Column(db.Integer, nullable=False)
    speed: int = db.Column(db.Integer, nullable=False)
    angle: int = db.Column(db.Integer, nullable=False)
    duration: int = db.Column(db.Integer, nullable=True)
    distance: int = db.Column(db.Integer, nullable=True)

 
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    session = db.relationship('Session', back_populates='commands')