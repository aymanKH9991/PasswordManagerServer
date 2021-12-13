from Messages import Message as Ms


class SessionMessage(Ms.Message):
    def __init__(self, session_key: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Session",
                    "SessionKey": session_key,
                }
            elif message["Type"] == "Session":
                super(SessionMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
