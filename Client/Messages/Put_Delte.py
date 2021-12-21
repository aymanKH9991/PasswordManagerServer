from Messages import Message as Ms


class PutDeleteMessage(Ms.Message):
    def __init__(self, tag, title: str, name: str, password: str, description: str, files: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Put-Delete",
                    "Title": title,
                    "Name": name,
                    "Password": password,
                    "Description": description,
                    "Files": files,
                    "Tag": tag
                }
            elif message['Type'] == "Put":
                super(PutDeleteMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
