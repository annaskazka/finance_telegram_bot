from app.models.user import User


class UserManager:
    def __init__(self):
        self.users = {}

    def get_user(self, user_id: int) -> User:
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        return self.users[user_id]
