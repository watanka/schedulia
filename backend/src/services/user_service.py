from src.db.base import DatabaseInterface

class UserService:
    def __init__(self, db: DatabaseInterface):
        self.db = db

