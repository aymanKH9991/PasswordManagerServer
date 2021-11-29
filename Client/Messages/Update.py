from Messages import Message as Ms


class UpdateMessage(Ms.Message):
    def __init__(self, id: int, new_password: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Update",
                    "Id": id,
                    "NewPassword": new_password
                }
            elif message["Type"] == "Update":
                super(UpdateMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
