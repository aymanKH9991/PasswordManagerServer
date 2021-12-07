import pymongo
from Crypto.Hash import SHA512


class DB:
    def __init__(self, data_base_name='SafePass'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[data_base_name]

    def get_db_name(self):
        return self.__DB.name + 'DB'

    async def insert_new_user(self, name: str, password: str, public_key: str):
        user_itr = self.__DB['Users'].find({'Name': name})
        if user_itr.count() != 0:
            for user in user_itr:
                if user['PublicKey'] == public_key:
                    return -1
        user = self.__DB['Users'].insert_one({
            'Name': name,
            'Password': password,
            'PublicKey': public_key
        })
        # password_hash = SHA512.new(password.encode('utf8'))
        # password_hash.update(public_key.encode('utf8'))
        # user = self.__DB['Users'].insert_one({
        #     'Name': name,
        #     'Password': password_hash.hexdigest(),
        #     'PublicKey': public_key
        # })
        # password_hash.update(user.inserted_id.__str__().encode('utf8'))
        # self.__DB['Users'].update_one(
        #     {'Name': name, 'PublicKey': public_key},
        #     {'$set': {'Password': password_hash.hexdigest()}}
        # )
        return 1

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def check_user(self, name, public_key):
        return self.query('Users', {'PublicKey': public_key, 'Name': name}).count() == 1