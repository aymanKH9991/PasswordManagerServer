from Messages import *
import Model.Model as model


class CMDInput:
    def __init__(self):
        self.Loged = False
        self.last_message = {}
        self.__DB = model.DB()

    def init_input_ui(self):
        try:
            input_str = input("<<Welcome To SafePassSystem>>\n"
                              + "1.SignUp\n" + "2.Login\n"
                              + "3.exit\n" + "Choose: ").lower()
            if input_str in ['signup', '1']:
                self.signup_ui()
            elif input_str in ['login', '2']:
                self.login_ui()
        except Exception as e:
            print(e)

    def signup_ui(self):
        print('signup')

    def login_ui(self):
        print('login')

    def operations_ui(self):
        try:
            input_str = input("<<Operations UI>>\n"
                              + "1.Add Password\n2.Get Password\n"
                              + "3.Update Password\n4.Delete Password\n5.exi\nt"
                              + "Choose: ").lower()
            if input_str in ['add', '1']:
                self.put_password_ui()
            elif input_str in ['get', '2']:
                self.get_password_ui()
            elif input_str in ['update', '3']:
                self.update_password_ui()
            elif input_str in ['delete', '4']:
                self.delete_password_ui()
            else:
                self.last_message = {"Type": "Finished"}
        except Exception as e:
            print(e)

    def put_password_ui(self):
        print('New Password')

    def get_password_ui(self):
        print('Get Password')

    def update_password_ui(self):
        print('Update Password')

    def delete_password_ui(self):
        print('Delete Password')
