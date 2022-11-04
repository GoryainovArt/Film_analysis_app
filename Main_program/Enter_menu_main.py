host = "127.0.0.1"
user = "root"
password = ""
db_name = "msd_users"

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from  PyQt5.QtWidgets import QMessageBox

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from Enter_menu import Ui_Form
from mail_bot import send_mail
from random import randint

import pymysql
try:
    main_connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
except:
    pass

class  Enter_menu_window(QWidget):
    def __init__(self, parent=None):
        super(Enter_menu_window,self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
        self.ui.stackedWidget.setCurrentIndex(1)
        self.checK_message = ''
        self.login = ''

        # Set Main background to transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # ХЗ, что это
        self.ui.pushButton_5.clicked.connect(lambda: self.pass_to_sign_up())
        self.ui.pushButton_6.clicked.connect(lambda: self.pass_to_reg())

        # Регистрация
        self.ui.pushButton.clicked.connect(lambda: self.registration())
        # Авторизация

        # Выход
        self.ui.pushButton_3.clicked.connect(lambda: self.close())

        # Назад
        self.ui.pushButton_8.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))

        self.ui.pushButton_9.clicked.connect(lambda: self.send_again())

        # Восстановление пароля
        self.ui.pushButton_4.clicked.connect(lambda: self.send_on_mail())
        self.ui.pushButton_7.clicked.connect(lambda: self.confirmation())
        pix = QPixmap('C:\\Users\\Home PC\\Desktop\\VKR_program\\Interface\\Cursor\\arrow.cur')
        coords = (3,3)
        cursor = QCursor(pix, *coords)
        self.setCursor(cursor)


        def MoveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
        self.ui.frame_2.mouseMoveEvent = MoveWindow

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()
        self.ui.widget.hide()
        self.ui.widget.show()

    def pass_to_reg(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.pushButton_6.setStyleSheet("background-color: rgb(0, 170, 255);")
        self.ui.pushButton_5.setStyleSheet("background-color: rgb(255, 255, 255);")

    def pass_to_sign_up(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.pushButton_5.setStyleSheet("background-color: rgb(0, 170, 255);")
        self.ui.pushButton_6.setStyleSheet("background-color: rgb(255, 255, 255);")

    def send_again(self):
        self.check_message = str(randint(100000, 1000000))
        try:
            with main_connection.cursor() as cursor:
                email_query = f"SELECT email FROM users_upd WHERE login = '{self.ui.lineEdit_5.text()}'"
                cursor.execute(email_query)
                print(3)
                send_mail(self.check_message, cursor.fetchone()['email'])
                self.login = self.ui.lineEdit_5.text()
        except:
            return


    def confirmation(self):
        if self.ui.lineEdit_7.text() != self.check_message:
            QMessageBox.about(self,'Уведомление','Ошибка.\nНеправильный код.')
        else:
            print('Классно')
            QMessageBox.about(self,'Уведомление','Успешная регистрация.')
            self.ui.stackedWidget.setCurrentIndex(1)
            try:
                with main_connection.cursor() as cursor:
                    # Получить email по логину
                    query = f"UPDATE `users_upd` SET users_upd.Verified=1 WHERE users_upd.login = '{self.login}'"
                    cursor.execute(query)
                    main_connection.commit()
            except:
                return


    def send_on_mail(self):
       with connection.cursor() as cursor:
            # Получить email по логину
            email_query = f"SELECT * FROM users_upd WHERE users_upd.login = '{self.ui.lineEdit_5.text()}'"
            cursor.execute(email_query)
            result = cursor.fetchone()
            message = "".join([result['password'][i] if i % 2 == 0 else "*" for i in range(len(result['password']))])
            send_mail(message,result["email"])


    def registration(self):
        self.login = self.ui.lineEdit.text()
        email = self.ui.lineEdit_2.text()
        password_1 = self.ui.lineEdit_3.text()
        password_2 = self.ui.lineEdit_4.text()

        # Проверка логина
        import re
        pattern = r"([a-zA-Z\d_]+)"
        res = re.search(pattern, self.login)
        print(res)
        if  not ((not res is None) and (res.group(1) == self.login) and (6 <= len(self.login) < 16)):
            QMessageBox.about(self,'Уведомление','Некорректный логин.\nЛогин может состоять из цифр,английских букв и символа "_".\nКоличество символов от 6 до 15.')
            return

        # Проверка пароля
        pattern = r"([a-zA-Z\d]+)"
        res = re.search(pattern, password_1)
        if not ((not res is None) and (res.group(1) == password_1) and (len(password_1) > 7)):
            QMessageBox.about(self,'Уведомление','Некорректный пароль.\nПароль должен состоять из цифр и английских букв.\nКоличество символов не менее 7.')
            return

        # Почта
        pattern = r"([a-zA-Z\d._]+@[a-z]+.[a-z]+)"
        res = re.search(pattern, email)
        if not ((not res is None) and (res.group(1) == email)):
            QMessageBox.about(self,'Уведомление','Некорректная почта.\nПочта должна быть следующиего вида:\nexample@gmail.com')
            return

        if password_1 != password_2:
            message = 'Пароли не совпадают'
            QtWidgets.QMessageBox.about(self,"Уведомление",message)
        else:
            try:
                with main_connection.cursor() as cursor:
                    # Проверка, есть ли уже такой login
                    user_list_query = f"SELECT EXISTS(SELECT * FROM users_upd WHERE users_upd.login = '{self.login}')"
                    cursor.execute(user_list_query)
                    if cursor.fetchone()[f"EXISTS(SELECT * FROM users_upd WHERE users_upd.login = '{self.login}')"]:
                        QtWidgets.QMessageBox.about(self,"Уведомление","Такой логин уже существует")
                    else:
                        # Добавить нового пользователя
                        add_user_query = f"INSERT INTO `users_upd`(login, password, email, Verified) values ('{self.login}', '{password_1}', '{email}',0);"
                        cursor.execute(add_user_query)
                        main_connection.commit()
                        QtWidgets.QMessageBox.about(self, "Уведомление", "Подтвердите регистрацию.")
                        self.ui.stackedWidget.setCurrentIndex(1)
                        self.ui.lineEdit.setText('')
                        self.ui.lineEdit_2.setText('')
                        self.ui.lineEdit_3.setText('')
                        self.ui.lineEdit_4.setText('')
                        # Отправить код верификации
                        self.check_message = str(randint(100000, 1000000))
                        send_mail(self.check_message, email)
                        self.ui.stackedWidget.setCurrentIndex(2)
            except:
                return
