from Messages import Message as Ms


class OldUserMessage(Ms.Message):
    def __init__(self, name: str, password: str, unique_key: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "OldUser",
                    "Name": name,
                    "Password": password,
                    "UniqueKey": unique_key
                }
            elif message['Type'] == "OldUser":
                super(OldUserMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
