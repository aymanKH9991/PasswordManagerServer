from Messages import Message as Ms


class CryptoMessage(Ms.Message):
    def __init__(self, name, enc_message, nonce, tag, message: dict = None):
        try:
            if message is None:
                self.message_info = {
                    "Type": "Encrypt",
                    "Name": name,
                    "Message": enc_message,
                    "Nonce": nonce,
                    "Tag": tag
                }
            elif message["Type"] == "Encrypt":
                super(CryptoMessage, self).__init__(message=message)
        except Exception as e:
            print(e)
