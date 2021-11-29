from Messages import Message as Ms


class DeleteMessage(Ms.Message):
    def __init__(self, id: int, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Delete",
                    "Id": id
                }
            elif message["Type"] == "Delete":
                super(DeleteMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
