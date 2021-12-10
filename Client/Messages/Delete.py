from Messages import Message as Ms


class DeleteMessage(Ms.Message):
    def __init__(self, title: str, name: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Delete",
                    "Name": name,
                    "Title": title
                }
            elif message["Type"] == "Delete":
                super(DeleteMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
