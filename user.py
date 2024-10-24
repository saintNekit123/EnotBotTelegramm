class User:
    user_dict: dict = dict()

    def __init__(self):
        self.chat_id = None
        self.id = None
        self.fullname = None
        self.phone = None
        self.linkT = None
    
    @classmethod
    def get_user(cls, id_user):
        """
        Метод для получения пользователя.
        Если пользователь существует в словаре, то возвращаем ссылку на него, если пользователя нет то
        создаем его и также возвращаем ссылку на пользователя.
        param id_user: ID Пользователя чата.
        """
        if id_user in User.user_dict:
            user = User.user_dict[id_user]
        else:
            user: object = User()
            User.user_dict[id_user] = user
        return user

