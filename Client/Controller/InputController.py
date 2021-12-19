import base64
import os
import pathlib
import sys

import Messages.NewUser
import Messages.OldUser
import Model.Model as model
import Messages.Put
import Messages.Update
import Messages.Delete
import Messages.Get
import Messages.Share


class CMDInput:
    def __init__(self,public_key=None):
        self.last_message = {}
        self.__DB = model.DB()
        self.user_name = None
        self.public_key = public_key

    def init_input_ui(self):
        try:
            input_str = input("<<Welcome To SafePassSystem>>\n"
                              + "1.SignUp\n" + "2.Login\n"
                              + "3.exit\n" + "Choose: ").lower()
            if input_str in ['signup', '1']:
                self.__signup_ui()
            elif input_str in ['login', '2']:
                self.__login_ui()
            else:
                sys.exit(0)
        except Exception as e:
            print(e)

    def __signup_ui(self):
        try:
            full_name = input('Full Name: ')
            password = input('Password: ')
            while len(password) < 8:
                password = input('At Lest 8\nPassword: ')
            ms = Messages.NewUser.NewUserMessage(full_name=full_name,
                                                 password=password,
                                                 unique_key=base64.b64encode(self.public_key).decode('utf8'))
            self.last_message = ms.to_json_string()
            print(self.last_message)
            self.user_name = full_name
        except Exception:
            sys.exit(-1)

    def __login_ui(self):
        users_name = self.__DB.get_users_name()
        if len(users_name) != 0:
            print('<<Registered Users>>')
            for i, name in enumerate(users_name):
                print(i, name)
        try:
            full_name = input('Name: ')
            if full_name in users_name:
                password = input('Password: ')
                while len(password) < 8:
                    password = input('At Lest 8\nPassword: ')
                user = self.__DB.query('Users', {'Name': full_name})
                ms = Messages.OldUser.OldUserMessage(name=full_name,
                                                     password=password,
                                                     unique_key=user[0]['PublicKey'])
                self.last_message = ms.to_json_string()
                self.user_name = full_name
            else:
                self.last_message = {
                    "Type": "Error",
                    "Description": "There No Such a User Name"
                }
        except Exception as e:
            print(e)
            sys.exit(-1)

    def operations_ui(self):
        try:
            input_str = input("<<Operations UI>>\n"
                              + "1.Add Password\n2.Get Password\n"
                              + "3.Update Password\n4.Delete Password\n"
                              + "5.Share Password\n6.exit\n"
                              + "Choose: ").lower()
            if input_str in ['add', '1']:
                self.__put_password_ui()
            elif input_str in ['get', '2']:
                self.__get_password_ui()
            elif input_str in ['update', '3']:
                self.__update_password_ui()
            elif input_str in ['delete', '4']:
                self.__delete_password_ui()
            elif input_str in ['share', '5']:
                self.__share_password_ui()
            else:
                sys.exit(0)
        except Exception as e:
            print(e)

    def __put_password_ui(self):
        name = self.user_name
        if name is None:
            self.last_message = {
                "Type": "Error",
                "Description": "Not Signed Up Or Logged In!!"
            }
            return
        title = input('Title: ')
        password = input('Password: ')
        description = input('Description: ')
        i = 1
        file_path = input(f'To add Files just type In path of File: \n{i}.')
        files = {}
        while True:
            if file_path == '' or file_path == '\n':
                break
            else:
                if file_path[0] == '"' and file_path[-1] == '"':
                    file_path = file_path[1:-1]
                if pathlib.Path.exists(pathlib.Path(file_path)):
                    if file_path.split('\\')[-1].split('.')[-1] == 'txt':
                        with open(file_path, 'r+', encoding='utf8') as file:
                            files[f'{i}'] = {
                                'FileName': file_path.split('\\')[-1],
                                'File': file.read()
                            }
                            i += 1
                    else:
                        print('only support txt file for Now')
                else:
                    print('File Not Exist')
            file_path = input(f'{i}.')
        ms = Messages.Put.PutMessage(title=title,
                                     name=name,
                                     password=password,
                                     description=description,
                                     files=files)
        self.last_message = ms.to_json_string()

    def __get_password_ui(self):
        if self.user_name is None:
            self.last_message = {
                "Type": "Error",
                "Description": "Not Signed Up Or Logged In!!"
            }
            return
        title = input('Title: ')
        ms = Messages.Get.GetMessage(title=title, name=self.user_name)
        self.last_message = ms.to_json_string()

    def __update_password_ui(self):
        name = self.user_name
        if name is None:
            self.last_message = {
                "Type": "Error",
                "Description": "Not Signed Up Or Logged In!!"
            }
            return
        title = input('New Title: ')
        old_title = input('Old Title: ')
        password = input('Password: ')
        description = input('Description: ')
        i = 1
        file_path = input(f'To add Files just type In path of File: \n{i}.')
        files = {}
        while True:
            if file_path == '' or file_path == '\n':
                break
            else:
                if file_path[0] == '"' and file_path[-1] == '"':
                    file_path = file_path[1:-1]
                if pathlib.Path.exists(pathlib.Path(file_path)):
                    if file_path.split('\\')[-1].split('.')[-1] == 'txt':
                        with open(file_path, 'r+', encoding='utf8') as file:
                            files[f'{i}'] = {
                                'FileName': file_path.split('\\')[-1],
                                'File': file.read()
                            }
                            i += 1
                    else:
                        print('only support txt file for Now')
                else:
                    print('File Not Exist')
            file_path = input(f'{i}.')
        ms = Messages.Update.UpdateMessage(title=title,
                                           old_title=old_title,
                                           name=name,
                                           password=password,
                                           description=description,
                                           files=files)
        self.last_message = ms.to_json_string()

    def __delete_password_ui(self):
        if self.user_name is None:
            self.last_message = {
                "Type": "Error",
                "Description": "Not Signed Up Or Logged In!!"
            }
            return
        title = input('Title: ')
        ms = Messages.Delete.DeleteMessage(title=title, name=self.user_name)
        self.last_message = ms.to_json_string()

    def __share_password_ui(self):
        try:
            if self.user_name is None:
                self.last_message = {
                    "Type": "Error",
                    "Description": "Not Signed Up Or Logged In!!"
                }
                return
            second_user = input('User Name You Like To Share With: ')
            title = input('New Title: ')
            password = input('Password: ')
            description = input('Description: ')
            i = 1
            file_path = input(f'To add Files just type In path of File: \n{i}.')
            files = {}
            while True:
                if file_path == '' or file_path == '\n':
                    break
                else:
                    if file_path[0] == '"' and file_path[-1] == '"':
                        file_path = file_path[1:-1]
                    if pathlib.Path.exists(pathlib.Path(file_path)):
                        if file_path.split('\\')[-1].split('.')[-1] == 'txt':
                            with open(file_path, 'r+', encoding='utf8') as file:
                                files[f'{i}'] = {
                                    'FileName': file_path.split('\\')[-1],
                                    'File': file.read()
                                }
                                i += 1
                        else:
                            print('only support txt file for Now')
                    else:
                        print('File Not Exist')
                file_path = input(f'{i}.')
            ms = Messages.Share.ShareMessage(title=title,
                                             name=self.user_name,
                                             second_user=second_user,
                                             password=password,
                                             description=description,
                                             files=files)
            self.last_message = ms.to_json_string()

        except Exception as e:
            print('Error In Share')
