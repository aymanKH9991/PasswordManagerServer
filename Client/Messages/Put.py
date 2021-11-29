from Messages import Message as Ms


class PutMessage(Ms.Message):
    def __init__(self, title: str, name: str, password: str, description: str, files: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Put",
                    "Title": title,
                    "Name": name,
                    "Password": password,
                    "Description": description,
                    "Files": files
                }
            elif message['Type'] == "Put":
                super(PutMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
