from Messages import Message as Ms


class GetMessage(Ms.Message):
    def __init__(self, title: str, name: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Get",
                    "Name": name,
                    "Title": title
                }
            elif message["Type"] == "Get":
                super(GetMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
