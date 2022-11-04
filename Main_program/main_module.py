import sys
from PyQt5.QtWidgets import QApplication
from Functions_module import MainWindow
from Enter_menu_main import Enter_menu_window
from  PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from random import randint

app = QApplication(sys.argv)
enter_window = Enter_menu_window()
enter_window.show()

import pymysql

host = "127.0.0.1"
user = "root"
password = ""
db_name = "msd_users"


try:
    main_connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print('successfully connected 2')
    print(28 * '-')
except:
    print('Ошбика')



def OpenWnd():
    print(enter_window.ui.lineEdit_5.text())
    print(enter_window.ui.lineEdit_6.text())

    try:
        with main_connection.cursor() as cursor:
            print('Шаг 1')
            # Проверка, есть ли такой id в базе данных
            user_list_query = f"SELECT EXISTS(SELECT * FROM users_upd WHERE users_upd.login = '{enter_window.ui.lineEdit_5.text()}')"
            print('Пошел процесс')
            cursor.execute(user_list_query)
            if not cursor.fetchone()[f"EXISTS(SELECT * FROM users_upd WHERE users_upd.login = '{enter_window.ui.lineEdit_5.text()}')"]:
                print('Шаг 2')
                enter_window.ui.lineEdit_5.setText('')
                enter_window.ui.lineEdit_6.setText('')
                print('В доступе отказано')
                qmb = QMessageBox()
                qmb.setWindowTitle('Ошибка входа')
                # frame_status.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
                qmb.setIcon(QMessageBox.Warning)
                qmb.setText('Такой логин не найден')
                qmb.setInformativeText('Проверьте правильность введенных данных')
                qmb.setStandardButtons(QMessageBox.Ok)
                qmb.exec_()
                return
            else:
                print(1)
                password_query = f"SELECT * FROM users_upd where users_upd.login = '{enter_window.ui.lineEdit_5.text()}'"
                cursor.execute(password_query)
                print(2)
                result = cursor.fetchone()
                if not result['password'] == enter_window.ui.lineEdit_6.text():
                    enter_window.ui.lineEdit_6.setText('')
                    print('Неправильный пароль_1')
                    qmb = QMessageBox()
                    qmb.setWindowTitle('Ошибка входа')
                    # frame_status.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
                    qmb.setIcon(QMessageBox.Warning)
                    qmb.setText('Неправильный пароль')
                    qmb.setInformativeText('Проверьте правильность введенных данных или запросите восстановление пароля на почту')
                    qmb.setStandardButtons(QMessageBox.Ok)
                    qmb.exec_()
                    return
                if not result['Verified'] == 1:
                    enter_window.ui.lineEdit_6.setText('')
                    print('Неправильный пароль_2')
                    qmb = QMessageBox()
                    qmb.setWindowTitle('Ошибка входа')
                    # frame_status.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
                    qmb.setIcon(QMessageBox.Warning)
                    qmb.setText('Аккаунт не подтвержден.')
                    qmb.setInformativeText('Пожалуйста, подтвердите аккаунт по почте.')
                    qmb.setStandardButtons(QMessageBox.Ok)
                    qmb.exec_()
                    enter_window.ui.stackedWidget.setCurrentIndex(2)

                    return

                # Если все нормально - создать основное окно
                print('Шаг 3')
                global main_window
                main_window = MainWindow(enter_window.ui.lineEdit_5.text())
                main_window.ui.pushButton_5.clicked.connect(lambda: exit())
                print('Шаг 4')
                enter_window.hide()
                main_window.show()
    except Exception as Ex:
        print(Ex)
        QtWidgets.QMessageBox.about(enter_window, "Уведомление",
                                    "Проблема с соединением. Проверьте подключение к сети")



def exit():
    enter_window.ui.lineEdit_5.setText('')
    enter_window.ui.lineEdit_6.setText('')
    enter_window.show()
    main_window.close()

# Обработка кнопки "Войти"
enter_window.ui.pushButton_2.clicked.connect(lambda: OpenWnd())

sys.exit(app.exec_())

