from Messages import Message as Ms


class ConfigMessage(Ms.Message):
    def __init__(self, public_key: str, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Config",
                    "PublicKey": public_key
                }
            elif message["Type"] == "Config":
                super(ConfigMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
