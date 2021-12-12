from Messages import Message as Ms


class UpdateMessage(Ms.Message):
    def __init__(self, title: str,old_title:str, name: str, password: str, description: str, files: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Update",
                    "Title": title,
                    "OldTitle":old_title,
                    "Name": name,
                    "Password": password,
                    "Description": description,
                    "Files": files
                }
            elif message["Type"] == "Update":
                super(UpdateMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
