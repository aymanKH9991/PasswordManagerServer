import json
import time

import pymongo
from Crypto.Hash import SHA512
import datetime


class DB:
    def __init__(self, data_base_name='SafePass'):
        __connection_db = pymongo.MongoClient()
        self.__DB = __connection_db[data_base_name]

    def get_db_name(self):
        return self.__DB.name + 'DB'

    def insert_new_user(self, name: str, password: str, public_key: str):
        user_itr = self.__DB['Users'].find({'Name': name})
        if user_itr.count() != 0:
            for user in user_itr:
                if user['PublicKey'] == public_key or user['Name'] == name:
                    return -1
        user = self.__DB['Users'].insert_one({
            'Name': name,
            'Password': SHA512.new(password.encode('utf8')).hexdigest(),
            'PublicKey': public_key
        })
        return 1

    def query(self, collection_name, query):
        return self.__DB[collection_name].find(query)

    def check_user(self, name, public_key):
        q_res = self.query('Users', {'PublicKey': public_key, 'Name': name})
        return [q_res[0], q_res.count() == 1]

    def add_active_user(self, name, public_key, peer):
        if not self.is_user_active(name):
            self.__DB['ActiveUsers'].insert_one({
                'Name': name,
                'PublicKey': public_key,
                'Peer': peer
            })

    def remove_active_users(self):
        self.__DB['ActiveUsers'].drop()

    def remove_active_user(self, name, public_key):
        if self.is_user_active(name):
            self.__DB['ActiveUsers'].delete_one({
                'Name': name,
                'PublicKey': public_key
            })

    def is_user_active(self, name):
        return self.query('ActiveUsers', {'Name': name}).count() == 1

    def get_user_by_peer(self, peer):
        return self.query('ActiveUsers', {"Peer": peer})

    def add_element(self, username, title, description, password, files):
        if self.is_user_active(username):
            self.__DB['Elements'].insert_one({
                'Title': title,
                'Name': username,
                'Password': password,
                'Description': description,
                'Files': files
            })
            return 1
        return -1

    def get_user_elements(self, name):
        return self.query('Elements', {'Name': name})

    def get_element_by_title(self, name, title):
        if self.is_user_active(name):
            res = self.query('Elements', {'Name': name, 'Title': title})
        return res

    def update_element(self, name, old_title, title, password, description, files):
        res = self.get_element_by_title(name, old_title)
        if res is None or res.count() == 0:
            return -1
        else:
            self.__DB['Elements'].update_many({'Name': name, 'Title': old_title}, {'$set': {
                "Title": title,
                "Name": name,
                "Password": password,
                "Description": description,
                "Files": files
            }})
            return 1

    def delete_element(self, name, title):
        res = self.get_element_by_title(name, title)
        if res is None or res.count() == 0:
            return -1
        else:
            self.__DB['Elements'].delete_many({'Name': name, 'Title': title})
            return 1

    def get_user_password(self, name):
        res = self.is_user_active(name)
        if res == 1:
            return self.query('Users', {'Name': name})[0]['Password']
        else:
            return -1

    def add_event(self, dic: dict):
        temp = {
            'Time': datetime.datetime.now().__str__()
        }
        for key, val in dic.items():
            temp[key] = val
        pubkey = self.get_user_publicKey(dic['Name'])
        temp['PublicKey'] = pubkey
        self.__DB['Events'].insert_one(temp)

    def get_user_events(self, user_name):
        return self.query('Events', {'UserName': user_name})

    def get_user_publicKey(self, user_name):
        res = self.query('Users', {'Name': user_name})
        return res[0]['PublicKey'] if res.count() == 1 else None

    def add_share_message(self, mes):
        try:
            res = mes if type(mes) == dict else json.loads(mes)
            ins_res = self.__DB['ShareMessages'].insert_one(res)
            return True
        except Exception as e:
            print('Add Share Message Error')
            return False

    def get_share_messages(self, user_name):
        try:
            res = []
            query = self.query('ShareMessages', {'SecondUser': user_name})
            for r in query:
                res.append(r)
            return res if len(res) > 0 else None
        except Exception as e:
            print('Get Share Messages Error')
            return None

    def delete_share_message(self, user_name, tag):
        try:
            res = self.__DB['ShareMessages'].delete_one({'SecondUser': user_name, 'Tag': tag})
            return True if res.deleted_count == 1 else False
        except Exception as e:
            print(e)
            return False
