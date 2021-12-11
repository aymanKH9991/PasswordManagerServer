from Messages import Message as Ms


class RespondMessage(Ms.Message):
    def __init__(self, details: dict, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Respond",
                    "Details": details
                }
            elif message["Type"] == "Respond":
                super(RespondMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
