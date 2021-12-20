import pymongo


class DB:
    def __init__(self, database_name='SafePassClient'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[database_name]

    def get_db_name(self):
        return self.__DB.name

    def insert_new_user(self, name: str, public_key: str, private_key: str):
        users = self.__DB['Users'].find({'Name': name})
        if users.count() != 0:
            for user in users:
                if user['PublicKey'] == public_key or user['Name'] == name:
                    return -1
        self.__DB['Users'].insert_one({
            'Name': name,
            'PublicKey': public_key,
            'PrivateKey': private_key
        })

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def get_users_name(self):
        return [user['Name'] for user in self.query('Users', {})]

    def get_public_key(self, username):
        res = self.query('Users', {
            'Name': username
        })
        return res[0]['PublicKey'] if res.count()==1 else None

    def get_private_key(self, username):
        res = self.query('Users', {
            'Name': username
        })
        return res[0]['PrivateKey'] if res.count()==1 else None
