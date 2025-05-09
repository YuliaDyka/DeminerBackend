from deminer import db
from .i_dto import IDto

class User(db.Model, IDto):
    __tablename__ = "user"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(45), nullable=False)
    email: str = db.Column(db.String(45), nullable=False)
    password: str = db.Column(db.String(45), nullable=False)

    def check_password(self, password):
        # TODO: Impement checking password logic!!!
        print("Checking password:", password)
        return True

