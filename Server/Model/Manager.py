class DBManager:
    def __init__(self):
        pass

    def add_db(self, db):
        self.__DB = db

    def drop_db(self):
        self.__DB.remove_active_users()

    def name(self):
        print(self.__DB.get_db_name())