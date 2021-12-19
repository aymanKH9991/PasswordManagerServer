from Messages import Message as Ms


class ShareMessage(Ms.Message):
    def __init__(self, title: str, name: str, second_user: str, password: str, description: str, files: dict,
                 message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Share",
                    "Title": title,
                    "Name": name,
                    "SecondUser": second_user,
                    "Password": password,
                    "Description": description,
                    "Files": files
                }
            elif message['Type'] == "Share":
                super(ShareMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
