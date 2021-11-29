import random

from Messages import Message as Ms
import time
import uuid


class NewUserMessage(Ms.Message):
    def __init__(self, full_name: str, password: str, unique_key: str = None, message: dict = None):
        if message is None:
            self.message_info = {
                "Type": "NewUser",
                "Name": full_name,
                "Password": password,
                "uniqueKey": unique_key if unique_key is not None else
                str(random.randint(0, time.time_ns())) +
                str(uuid.getnode()) +
                str(random.randint(0, time.time_ns()))
            }
        elif message['Type'] == 'NewUser':
            super(NewUserMessage, self).__init__(message)
