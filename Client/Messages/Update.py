from Messages import Message as Ms


class UpdateMessage(Ms.Message):
    def __init__(self, title: str, name: str, password: str, description: str, files: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Update",
                    "Title": title,
                    "Name": name,
                    "NewPassword": password,
                    "Description": description,
                    "Fiels": files
                }
            elif message["Type"] == "Update":
                super(UpdateMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
