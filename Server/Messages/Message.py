import json


class Message:
    def __init__(self, message: dict = None):
        self.message_info = message

    def to_json_byte(self):
        try:
            if self.message_info is None:
                raise Exception("Message Are None Or Something has been Missed")
            return json.dumps(self.message_info).encode(encoding='utf-8')
        except Exception as e:
            print(e)

    def to_json_string(self):
        try:
            if self.message_info is None:
                raise Exception("Message Are None Or Something has been Missed")
            return json.dumps(self.message_info)
        except Exception as e:
            print(e)
