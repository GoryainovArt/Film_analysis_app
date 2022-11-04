# Используемые библиотеки
import sys
import csv
import os
import time

import numpy as np
import requests
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
import matplotlib.pyplot as plt
from  PyQt5.QtWidgets import QMessageBox
import statistics as stats


# Графики
from Charts import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QBarSet, \
    QPercentBarSeries, QBarCategoryAxis, QBarSeries

# Модуля для корректировки фото
from Pillow_module import *
from KP_vote_parser import *


# Модули интерфейсов
from interface import Ui_MainWindow
from Film_window import CoordWidget
from Similar_request_widget import Widget_1
from nothing_request_widget import Widget_2

from Interests import Interest # Для области интересов
from Features_main import Features_window
from Connect_main import Connection_error_wnd
from  Interests_not_defined_main import Interests_not_defined_wdgt


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# Библиотеки для обучения моделей
# KNN
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

# Linear Regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso

# Gradient descent
from sklearn.linear_model import SGDRegressor

# Random forest
from sklearn.ensemble import RandomForestRegressor

# Вывод уведомления
def Message_box(WindowTitle=None, Icon=None, text=None, InformativeText=None, Buttons=None):
    qmb = QMessageBox()
    qmb.setWindowTitle(WindowTitle)
    # frame_status.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
    if Icon == 1:
        qmb.setIcon(QMessageBox.Warning)
    qmb.setText(text)
    qmb.setInformativeText(InformativeText)
    if Buttons == 1:
        qmb.setStandardButtons(QMessageBox.Ok)
    qmb.exec_()

# Уведомление о разрыве соединения с QMessageBox
def Disconnect():
    error = QtWidgets.QMessageBox()
    error.setWindowTitle('Уведомление')
    error.setText("Ошибка подключения.\nПожалуйста, проверьте свое интернет-соединение.")
    error.setIcon(QMessageBox.Warning)
    error.setStandardButtons(QMessageBox.Yes)
    error.exec_()

# Уведомление о разрыве соединения с пользовательским интерфейсом
def Connect_error_proc():
    app = QApplication(sys.argv)
    error = Connection_error_wnd()
    error.show()
    sys.exit(app.exec_())

# Процедура показа уведомления с задаваемым текстом
def Error_1(txt):
    error = Connection_error_wnd()
    error.ui.label.setText(txt)
    error.show()

# Соединение с базой данных
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
except:
    Connect_error_proc()

# Функция для формирования последовательности в методе Градиентный спуск
def lst(x,y,step):
    x = 0.001
    y = 100
    lst = [x, ]
    while x < y:
        lst.append(x * step)
        x = x * step
    return lst

# Функция для загрузки в базу данных гиперпараметров для алгоритма машинного обучения
# Входные параметры: название метода в базе данных, словарь гиперпараметров, логин пользователя
def work_with_db(method_name,info,user_id):
    with main_connection.cursor() as cursor:
        query = f"SELECT EXISTS(SELECT {method_name} FROM users_upd WHERE login ='{user_id}')"
        cursor.execute(query)
        if cursor.fetchone():
            # UPDATE
            query = f"UPDATE `users_upd` SET users_upd.{method_name}='{info}'  WHERE users_upd.login = '{user_id}'"
            cursor.execute(query)
            main_connection.commit()
        else:
            # Insert
            query = f"INSERT INTO `users_upd`({method_name}) values ({info}) WHERE users_upd.login = '{self.personal_id}'"
            cursor.execute(query)
            main_connection.commit()

# Функция проверки поля ввода на тип int и float. Если не один из них, то возвращает FALSE
def float_or_int(x):
    try:
        if float(x) or int(x):
            return 1
    except:
        return 0

# Функция проверки на наличия загруженного набора данных о пользователе, и не пустых полей ввода с правильными типами int или float
def Error_check(using_frame,*lineEdit_lst):
    if any(map(lambda x: 1 if x.text()=="" else 0,lineEdit_lst)):
        Error_1('Ошибка ввода.\nПожалуйста, заполните все поля.')
        return 0
    if not all(map(lambda x: 1 if float_or_int(x.text()) else 0,lineEdit_lst)):
        Error_1('Ошибка ввода.\nЗначения должны быть числами.')
        return 0
    else:
        if using_frame.empty:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
            return 0
        else:
            return 1

# Класс главного окна
class MainWindow(QMainWindow):
    def __init__(self, personal_id):
        super(MainWindow,self).__init__(parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) # Создание атрибута для хранения интерфейса
        self.personal_id = personal_id # Логин пользователя
        self.chart_1_counter = 0 # Счетчик количества построенных графиков.Значения могут быть 0 и 1. Больше нельзя строить
        self.chart_2_counter = 0
        self.chart_3_counter = 0
        self.chart_4_counter = 0
        self.chart_5_counter = 0
        self.chart_6_counter = 0
        self.chart_7_counter = 0
        self.Chart_list = [lambda: self.ui.stackedWidget_2.setCurrentIndex(0),
                      self.Vote_by_genres, self.Chart_1, self.Chart_2,
                      self.Chart_4, self.Chart_5, self.Chart_6, self.Chart_7] # Список всех графиков для перемещения с использованием кнопок "Вперед" и "Назад"

        self.ui.stackedWidget.setCurrentIndex(0)
        self.using_regression_method = ""
        self.using_clustering_method = ""
        self.user_frame = pd.DataFrame()    # Загруженный набор данных о пользователе
        self.full_frame = 0                 # Полный нормализованный набор данных о пользователе
        self.not_normalized_full_frame = 0  # Полный ненормализованный набор данных о пользователе
        self.predictable_film = ""          # Идентификатор фильма для прогнозирования оценки
        self.frame_separator = 0.8          # Размер обучающей выборки
        self.reserved_full_frame = 0        # Резервная копия полного нормализованного набора данных о пользователе


        # Наборы данных
        self.not_normalized_frame = pd.read_csv("C:/Users/Home PC/Desktop/Python/VKR/Parsing_dataset/upd_not_normalized_frame.csv", sep=",")
        self.normalized_frame = pd.read_csv("C:/Users/Home PC/Desktop/Python/VKR/Parsing_dataset/upd_normalized_frame.csv",sep=",")

        # Создать признак "Название фильма в нижнем регистре"
        self.not_normalized_frame["lower_title"] = self.not_normalized_frame["title"].apply(lambda x: x.lower())

        self.reserved_normalized_frame = self.normalized_frame
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Убрать Windows рамку кнопок
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.pushButton_7.clicked.connect(lambda: self.menu())  # Управление боковым меню

        # Системные кнопки управления
        self.ui.pushButton.clicked.connect(lambda: self.showMinimized())
        self.ui.pushButton_2.clicked.connect(lambda: self.maximize_button())
        self.ui.pushButton_3.clicked.connect(lambda: self.close())


        # Курсор
        pix = QPixmap('C:\\Users\\Home PC\\Desktop\\VKR_program\\Interface\\Cursor\\arrow.cur')
        coords = (3,3)
        cursor = QCursor(pix, *coords)
        self.setCursor(cursor)

        self.add_functions()
        # Для перемещения приложения по экрану
        def MoveWindow(e):
            if self.isMaximized() == False:
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
        self.ui.header_frame.mouseMoveEvent = MoveWindow

        # Создание персональной папки для хранения всех файлов
        if not os.path.exists(f"Users/User_{self.personal_id}"):
            os.makedirs(f"Users/User_{self.personal_id}")

        # Отображаемые признаки. По умолчанию выбраны все признаки
        buf_str = "По умолчанию.\n1. Год выхода\n2. Средняя оценка на Кинопоиске\n3. Количество оценок на Кинопоиске\n4. Средняя оценка на IMDb\n5. Количество оценок на IMDb\n6. Оценка критиков\n" \
                  "7. Количество оценок критиков\n8. Количество оценок критиков.\n9. Продолжительность\n10. Количество премий Оскар\n11. Количество номинаций на Оскар.\n12. Количество других премий\n13. Количество других номинаций\n" \
                  "14. Место в рейтинге ТОП250\n15. Десятилетие выхода\n16. Жанры\n17. Страна"
        self.ui.textEdit_5.setText(buf_str)
        self.ui.textEdit_3.setText(buf_str)
        self.ui.textEdit_7.setText(buf_str)
        self.ui.textEdit_17.setText(buf_str)

        # Отображение информации о пользователе
        with main_connection.cursor() as cursor:
            User_info_query = f"SELECT * FROM `users_upd` WHERE users_upd.login = '{self.personal_id}'"
            cursor.execute(User_info_query)
            rows = cursor.fetchall()[0]
            self.ui.label_4.setText(f'Nickname: {rows["name"]}') # Имя
            self.ui.label_3.setText(f'ID: {rows["kp_id"]}')      # Идентификатор

            # Еще фотография
            # Проверка, есть ли уже скачанная готовая фотография
            flag = False
            if not os.path.exists(f"Users/User_{self.personal_id}/Profile_photo.png"):
                # Скачать из бд
                result = rows["photo"]
                if not result is None:
                    with open(f"Users/User_{self.personal_id}/Profile_photo.png", 'wb') as file:
                        file.write(result)
                else:
                    self.ui.label_7.setPixmap(QtGui.QPixmap(f"Pics/incognito_upd.png"))
                    flag = True

            # Если нет обработанного изображения
            if not (os.path.exists(f"Users/User_{self.personal_id}/Profile_photo_upd.png")) and (not flag):
                # Обработать изображение
                modify_photo(f"Users/User_{self.personal_id}/Profile_photo.png")

            # Отобразить изображение
            if not flag:
                self.ui.label_7.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/Profile_photo_upd.png"))

            self.ui.radioButton_5.setChecked(True)

            # Загрузить Область интересов
            try:
                query = f"SELECT * FROM user_interests LEFT JOIN interests ON (user_interests.Interest_id =interests.Interest_id) WHERE login = '{self.personal_id}'"
                cursor.execute(query)
                res = cursor.fetchall()
                if len(res) == 0:
                    wdgt = Interests_not_defined_wdgt()
                    self.ui.horizontalLayout_94.addWidget(wdgt)
                else:
                    count = 0
                    for i in res:
                        count += 1
                        inter = Interest()
                        inter.ui.label_6.setText('Десятилетие: ' + str(i['Decade']))
                        inter.ui.label.setText(f'Интересы. Список {count}')
                        inter.ui.label_2.setText(f'Интересы. Список {count}')
                        self.ui.horizontalLayout_94.addWidget(inter)

                        if i['Top']:
                            inter.ui.label_8.setText('Предпочтительно фильмы из ТОП250')
                        else:
                            inter.ui.label_8.setText('Предпочтительно фильмы не из ТОП250')

                        if i['Oscar']:
                            inter.ui.label_5.setText('Есть премия Оскар')
                        else:
                            inter.ui.label_5.setText('Без премии Оскар')

                        import ast
                        genres_list = ast.literal_eval(i['Genres'])
                        for z in range(len(genres_list)):
                            if z == 0:
                                inter.ui.label_3.setText('Жанр: ' + genres_list[z])
                            else:
                                buffer = inter.ui.label_3.text()
                                inter.ui.label_3.setText(buffer + ", " + genres_list[z])

                        import ast
                        countries_list = ast.literal_eval(i['Countries'])
                        for z in range(len(countries_list)):
                            if z == 0:
                                inter.ui.label_7.setText('Страна: ' + countries_list[z])
                            else:
                                buffer = inter.ui.label_7.text()
                                inter.ui.label_7.setText(buffer + ", " + countries_list[z])

                        inter.ui.label_4.setText(
                            f"Продолжительность: больше 120 минут - {i['Time1']}%,\n"
                            f"от 90 до 120 минут - {i['Time2']}%,\n"
                            f"меньше 90 минут - {i['Time3']}%")
            except:
                Connect_error_proc()

            # Если есть файлы с графиками на компьютере, то выставить их сразу
            if os.path.exists(f"Users/User_{self.personal_id}/rand_chart_1.png"):
                self.ui.label_163.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/rand_chart_1.png'))
            else:
                self.ui.label_163.setText('Данный график еще не построен')
            if os.path.exists(f"Users/User_{self.personal_id}/rand_chart_2.png"):
                self.ui.label_165.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/rand_chart_2.png'))
            else:
                self.ui.label_165.setText('Данный график еще не построен')

            # Гистограмма оценок:
            if (os.path.exists(f"Users/User_{self.personal_id}/hist_vote.png")):
                self.ui.label_143.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/hist_vote.png"))

            # Графики кластеризации
            if (os.path.exists(f"Users/User_{self.personal_id}/k_means_matrix.png")):
                self.ui.label_79.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/k_means_matrix.png"))

            if (os.path.exists(f"Users/User_{self.personal_id}/Hierarchical_matrix.png")):
                self.ui.label_45.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/Hierarchical_matrix.png"))

            if (os.path.exists(f"Users/User_{self.personal_id}/DBSCAN.png")):
                self.ui.label_132.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/DBSCAN.png"))

            if os.path.exists(f"Users/User_{self.personal_id}/rand_chart_2.png"):
                self.ui.label_165.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/rand_chart_2.png'))


            # Список "Смотреть позже"
            user_list_query = f"SELECT id FROM user_library WHERE login ='{self.personal_id}' AND WatchList = 1"
            cursor.execute(user_list_query)
            self.ui.pushButton_65.setText(str(len(cursor.fetchall())))

            # Фильмы, загруженные в базу данных
            user_list_query = f"SELECT id FROM user_library WHERE user_library.login ='{self.personal_id}' AND WatchList = 0"
            cursor.execute(user_list_query)
            self.ui.pushButton_62.setText(str(len(cursor.fetchall())))

    # Кнопка изменения режима отображения
    # Либо перейти в полноэкранный режим, либо в оконный
    def maximize_button(self):
        if self.isMaximized() == True:
            self.showNormal()
        else:
            self.showMaximized()


    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    # Перемещение бокового меню
    def menu(self):
        width = self.ui.slide_menu_container.width()
        if self.ui.slide_menu_container.width() == 0:
            newWidth = 250
        else:
            newWidth = 0

        self.animation = QPropertyAnimation(self.ui.slide_menu_container, b"maximumWidth")
        self.animation.setDuration(100)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    # Связать обработчики нажатия кнопок с кнопками
    def add_functions(self):
        # Кнопки перехода по страницам меню
        self.ui.pushButton_8.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_9.clicked.connect(lambda: self.foo1())
        self.ui.pushButton_10.clicked.connect(lambda: self.pass_to_statistics())
        self.ui.pushButton_11.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

        # Переходы по вкладке "Прогнозирование"
        self.ui.pushButton_12.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.pushButton_13.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))
        self.ui.pushButton_14.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(6))
        self.ui.pushButton_20.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(7))
        self.ui.pushButton_61.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(8))
        self.ui.pushButton_74.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(14))


        # Переходы по вкладке "Сферы интересов"
        self.ui.pushButton_15.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(9))
        self.ui.pushButton_16.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(10))
        self.ui.pushButton_17.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(11))
        self.ui.pushButton_39.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(12))

        # Переход на страницу "Профиль"
        self.ui.pushButton_18.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(13))

        # Переход на страницу "Статистика"
        self.ui.pushButton_41.clicked.connect(lambda: self.Vote_by_genres())
        self.ui.pushButton_50.clicked.connect(lambda: self.Chart_1())
        self.ui.pushButton_51.clicked.connect(lambda: self.Chart_2())
        self.ui.pushButton_53.clicked.connect(lambda: self.Chart_4())
        self.ui.pushButton_54.clicked.connect(lambda: self.Chart_5())
        self.ui.pushButton_55.clicked.connect(lambda: self.Chart_6())
        self.ui.pushButton_56.clicked.connect(lambda: self.Chart_7())

        # Главное меню статистики
        self.ui.pushButton_57.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))

        # Кнопки вперед/назад для перехода между графиками
        self.ui.pushButton_29.clicked.connect(lambda: self.btn_back())
        self.ui.pushButton_30.clicked.connect(lambda: self.btn_next())

        # Кнопка "Поиск" для поиска фильмов
        self.ui.pushButton_6.clicked.connect(lambda: self.search_button())

        # Прогнозирование оценки
        self.ui.pushButton_46.clicked.connect(lambda: self.predict_vote_page())

        # Кнопка "Назад ко всем фильмам"
        self.ui.pushButton_64.clicked.connect(lambda: self.ui.stackedWidget_3.setCurrentIndex(0))

        # Кнопка, которая выводит QMessageBox о качестве набора фильмов
        self.ui.pushButton_62.clicked.connect(lambda: self.call_QMB())

        # Кнопка "показать график пользователя"
        self.ui.pushButton_73.clicked.connect(lambda: self.show_user_chart())

        # Автоматический подбор алгоритма машинного обучения
        self.ui.pushButton_80.clicked.connect(lambda: self.auto_search_params())


        # KNN
        self.ui.pushButton_31.clicked.connect(lambda: self.KNN(flag=True)) # Сохранить
        self.ui.pushButton_28.clicked.connect(lambda: self.KNN(flag=False)) # Предтестирование

        # Linear regression
        self.ui.pushButton_33.clicked.connect(lambda: self.linear_regression(flag=True)) # Сохранить параметры
        self.ui.pushButton_32.clicked.connect(lambda: self.linear_regression(flag=False)) # Предтестирование

        # Gradient descent
        self.ui.pushButton_79.clicked.connect(lambda: self.Gradient_descent(flag=False)) # Предтестирование
        self.ui.pushButton_81.clicked.connect(lambda: self.Gradient_descent(flag=True)) # Сохранить

        # Random forest
        self.ui.pushButton_71.clicked.connect(lambda: self.Random_forest(flag=True)) # Сохранить параметры
        self.ui.pushButton_72.clicked.connect(lambda: self.Random_forest(flag=False)) # Предтестирование

        # K-Means
        self.ui.pushButton_40.clicked.connect(lambda: self.use_elbow_method()) # Применить метод локтя
        self.ui.pushButton_19.clicked.connect(lambda: self.KMeans(True)) # Сохранить результаты
        self.ui.pushButton_45.clicked.connect(lambda: self.KMeans(False)) # Предтестирование


        # Иерархическая кластеризация
        self.ui.pushButton_63.clicked.connect(lambda: self.dendr()) # Вывод дендрограммы
        self.ui.pushButton_68.clicked.connect(lambda: self.Hierarchical(False)) # Предтестирование
        self.ui.pushButton_69.clicked.connect(lambda: self.Hierarchical(True)) # Сохранить метод как основной

        # DBSCAN
        self.ui.pushButton_59.clicked.connect(lambda: self.DBSCAN(True)) # Сохранить результаты
        self.ui.pushButton_58.clicked.connect(lambda: self.DBSCAN(False)) # Предтестирование DBSCAN



        # Выбор алгоритма прогнозирования
        self.ui.radioButton.clicked.connect(lambda: self.select_KNN())                 # Выбрать KNN (К-ближайших соседей)
        self.ui.radioButton_2.clicked.connect(lambda: self.select_linear_regression()) # Выбрать Linear regression (линейная регрессия)
        self.ui.radioButton_3.clicked.connect(lambda: self.select_gradient_descent())  # Выбрать Gradient descent (градиентный спуск)
        self.ui.radioButton_12.clicked.connect(lambda: self.select_random_forest())    # Выбрать Random forest (случайный лес)


        # Выбор алгоритма кластеризации
        self.ui.radioButton_7.clicked.connect(lambda: self.select_KMeans())            # Выбрать K-Means (К-средних)
        self.ui.radioButton_8.clicked.connect(lambda: self.select_hieararchical())     # Выбрать Hierarchical (Иерархическая кластеризация)
        self.ui.radioButton_9.clicked.connect(lambda: self.select_DBSCAN())            # Выбрать DBSCAN

        # Прогнозирование оценки
        self.ui.pushButton_49.clicked.connect(lambda: self.predict_vote())

        # Вызов окна с признаками
        self.ui.pushButton_26.clicked.connect(lambda: self.show_features_menu())

        # Кнопка для кластеризации
        self.ui.pushButton_43.clicked.connect(lambda: self.make_clustering())

        # Кнопка "Добавить id Кинопоиска"
        self.ui.pushButton_44.clicked.connect(lambda: self.add_kp_id())

        # Кнопка "Редактировать имя"
        self.ui.pushButton_34.clicked.connect(lambda: self.change_name())

        # Кнопка "Изменить пароль"
        self.ui.pushButton_35.clicked.connect(lambda: self.change_password())

        # Кнопка "Изменить почту"
        self.ui.pushButton_36.clicked.connect(lambda: self.change_email())

        # Кнопка добавить в список "Смотреть позже"
        self.ui.pushButton_67.clicked.connect(lambda: self.add_to_watch())

        # Кнопка удалить из списка "Смотреть позже"
        self.ui.pushButton_66.clicked.connect(lambda: self.delete_from_watch())

        # Кнопка показать весь список "Смотреть позже"
        self.ui.pushButton_23.clicked.connect(lambda: self.show_watch_list())

        # Кнопка показать весь список "Смотреть позже"
        self.ui.pushButton_37.clicked.connect(lambda: self.clean_watch_list())

        # Кнопка "Изменить фотографию"
        self.ui.pushButton_42.clicked.connect(lambda: self.change_photo())

        # Кнопка "Загрузить информацию с сайта 'Кинопоиск' "
        self.ui.pushButton_60.clicked.connect(lambda: self.load_KP_user_info())

        # Кнопка Текущее количество фильмов в списке "Смотреть Позже"
        self.ui.pushButton_65.clicked.connect(lambda: self.call_QMB_2())

        # Кнопка "Загрузить в базу данных информацию пользователя"
        self.ui.pushButton_75.clicked.connect(lambda: self.load_user_info_to_db())

        # Кнопка "Загрузить в базу данных информацию пользователя"
        self.ui.pushButton_76.clicked.connect(lambda: self.show_user_info_from_db())

        # Кнопки выбора источника загрузки данных
        self.ui.radioButton_10.clicked.connect(lambda: self.use_db())
        self.ui.radioButton_11.clicked.connect(lambda: self.use_csv())
        self.ui.radioButton_13.clicked.connect(lambda: self.use_kp())

        # Кнопка для выбора обычной регрессии
        self.ui.radioButton_4.clicked.connect(lambda: self.standart_regression())     # Сделать активной кнопку стандарнтной линейной регрессии
        self.ui.radioButton_5.clicked.connect(lambda: self.standart_regression_off()) # Сделать неактивной кнопку стандарнтной линейной регрессии
        self.ui.radioButton_6.clicked.connect(lambda: self.standart_regression_off()) # Сделать неактивной кнопку стандарнтной линейной регрессии

        # Кнопка "Графики для Random forest"
        self.ui.pushButton_38.clicked.connect(lambda: self.Random_forest_chart_1()) # Зависимость MSE от количества деревьев
        self.ui.pushButton_27.clicked.connect(lambda: self.Random_forest_chart_2()) # Зависимость MSE от количества признаков для разбиения

        # Для linear regression
        self.ui.checkBox_2.clicked.connect(lambda: self.Lock_standart_lr())        # Заблокировать возможность выбирать стандартную

        # Показать сохраненные в базе данных гиперпараметры
        self.ui.pushButton_82.clicked.connect(lambda: self.show_method_params())

        # Изменить процентное разбиение на обучающую и тестовую выборку)
        self.ui.pushButton_77.clicked.connect(lambda: self.separ())

        # Построить график линейной зависимости оценки
        self.ui.pushButton_21.clicked.connect(lambda: self.tth())

    # Функция построения графика линейной зависимости оценки от других признаков
    def tth(self):
        from sklearn.decomposition import PCA

        pca = PCA(n_components=1)
        pca.fit(self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False))
        pca_data = pca.transform(self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False))
        plt.figure(figsize=(10, 7))
        plt.yticks(range(0,11))
        plt.scatter(pca_data[:, 0], self.full_frame['vote'].values)
        plt.show()



    # Задать размер обучеющей выборки
    def separ(self):
        if (self.ui.lineEdit_27.text() != ''):
            if (float_or_int(self.ui.lineEdit_27.text())) and (0 < float(self.ui.lineEdit_27.text()) < 1):
                self.frame_separator = float(self.ui.lineEdit_27.text())
                return
            Error_1('Ошибка.\nЗначение должно быть десятичным числом.')
        else:
            Error_1('Ошибка.\nПожалуйста, заполните все поля.')

    # Загрузить информацию со страницы сайта "Кинопоиск" напрямую
    def load_KP_user_info(self):
        # Получить ID Кинопоиска
        with main_connection.cursor() as cursor:
            query = f"SELECT kp_id from users_upd WHERE users_upd.login = '{self.personal_id}'"
            cursor.execute(query)
            kp_id = cursor.fetchone()['kp_id']
        if kp_id is None:
            Error_1('Ошибка.\nПожалуйста, сначала сохраните ID с сайта Кинопоиск')
        else:
            import requests
            from bs4 import BeautifulSoup
            rq = f"https://www.kinopoisk.ru/user/{kp_id}/"
            response = requests.get(rq)
            if response.status_code == 404:
                Error_1('Кажется что-то пошло не так.\nПовторите попытку позже.')
            else:
                soup = BeautifulSoup(response.text, "lxml")
                if soup.find("html")["prefix"] == "og: http://ogp.me/ns#":
                    Error_1('Кажется что-то пошло не так.\nПовторите попытку позже.')
                else:
                    buf_1 = soup.find("div", class_="nick_name").string
                    buf_2 = soup.find("img", id='avatar_f')['src']
                    response = requests.get(buf_2)
                    img_option = open(f'Users/User_{self.personal_id}/Profile_photo.png', "wb")
                    img_option.write(response.content)
                    img_option.close()
                    modify_photo(f'Users/User_{self.personal_id}/Profile_photo.png')
                    self.ui.label_7.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/Profile_photo_upd.png"))
                    self.ui.label_4.setText(f"Nickname: {buf_1}")
                    try:
                        with main_connection.cursor() as cursor:
                            query = f"UPDATE `users_upd` SET users_upd.name='{buf_1}'  WHERE users_upd.login = '{self.personal_id}'"
                            cursor.execute(query)
                            main_connection.commit()
                            with open(f'Users/User_{self.personal_id}/Profile_photo.png', 'rb') as file:
                                BinaryData = file.read()
                            query = f"UPDATE `users_upd` SET users_upd.photo=%s  WHERE users_upd.login = '{self.personal_id}'"
                            cursor.execute(query, (BinaryData,))
                            main_connection.commit()
                    except:
                        Connect_error_proc()

    # Показать сохраненные в базе данных гиперпараметры
    def show_method_params(self):
        try:
            with main_connection.cursor() as cursor:
                query = f"SELECT * FROM users_upd WHERE login = '{self.personal_id}'"
                cursor.execute(query)
                result = cursor.fetchone()
                if not result['knn_method'] is None:
                    self.ui.textEdit_12.setText(F"KNN\n{result['knn_method']}\n \n")
                if not result['lr_method'] is None:
                    self.ui.textEdit_12.setText(self.ui.textEdit_12.toPlainText() + f"Linear regression\n{result['lr_method']}\n \n")
                if not result['gd_method'] is None:
                    self.ui.textEdit_12.setText(self.ui.textEdit_12.toPlainText() + f"Gradient descent\n{result['gd_method']}\n \n")
                if not result['rf_method'] is None:
                    self.ui.textEdit_12.setText(self.ui.textEdit_12.toPlainText() + f"Random forest\n{result['rf_method']}")
        except:
            Connect_error_proc()

    # Заблокировать использование стандартной регрессии
    def Lock_standart_lr(self):
        self.ui.lineEdit_44.setText('')
        if self.ui.radioButton_4.isEnabled():
            self.ui.radioButton_4.setEnabled(False)
        else:
            self.ui.radioButton_4.setEnabled(True)

    # Сделать кнопку стандартной регресии активной
    def standart_regression(self):
        self.ui.lineEdit_44.setText('')
        self.ui.lineEdit_44.setReadOnly(True)
        self.ui.lineEdit_44.setStyleSheet("background-color: rgb(167, 167, 167);")

    # Сделать кнопку стандартной регресии неактивной
    def standart_regression_off(self):
        self.ui.lineEdit_44.setReadOnly(False)
        self.ui.lineEdit_44.setStyleSheet("background-color: rgb(255, 255, 255);")

    # Использовать CSV-файл для загрузки информации о пользователе
    def use_csv(self):
        if self.ui.radioButton_11.isChecked():
            self.ui.label_10.setStyleSheet("border-bottom: 2px solid black;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_148.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_11.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.radioButton_10.setChecked(False)
            self.ui.radioButton_13.setChecked(False)
            res = self.open_file()
            self.reserved_full_frame = self.full_frame.copy()
            if res is None:
                self.ui.radioButton_11.setChecked(False)
                self.ui.label_10.setStyleSheet("border-bottom: initial;"
                                                'font: 75 13pt "Arial";')
                error = Connection_error_wnd()
                error.ui.label.setText('Файл не выбран.')
                error.show()
            if res == 1:
                pass
                ##
        else:
            self.ui.textEdit.setText('')
            self.user_frame = pd.DataFrame()
            self.full_frame = pd.DataFrame()
            self.not_normalized_full_frame = pd.DataFrame()
            self.ui.label_10.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
    # Использовать сайт "Кинопоиска" для загрузки информации об оцененных фильмах напрямую
    def use_kp(self):
        if self.ui.radioButton_13.isChecked():
            self.ui.label_11.setStyleSheet("border-bottom: 2px solid black;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_148.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_10.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.radioButton_10.setChecked(False)
            self.ui.radioButton_11.setChecked(False)
            import os
            path = f'Users/User_{self.personal_id}/KP_{self.personal_id}.csv'
            if (not os.path.exists(path)) or (os.path.getsize(path) == 0):
                Error_1('Такого файла нет. Нормальное выполнение')
            else:
                confirmation = QtWidgets.QMessageBox()
                confirmation.setWindowTitle('Уведомление')
                confirmation.setText("Ранее вы уже загружали в файл информацию из своего профиля на сайте 'Кинопоиск'. Перезаписать этот файл? Иначе будет использован имеющийся файл.\n\nПредупреждение:\nНе рекомендуется загружать более 10000 фильмов напрямую с сайта 'Кинопоиск'. Во избежание различных ошибок, загружайте большие данные через CSV файл.")
                confirmation.setStandardButtons(QMessageBox.No | QMessageBox.Yes| QMessageBox.Cancel)
                confirmation.buttonClicked.connect(self.YesNoRewrite)
                confirmation.exec_()
        else:
            self.ui.textEdit.setText('')
            self.user_frame = pd.DataFrame()
            self.full_frame = pd.DataFrame()
            self.not_normalized_full_frame = pd.DataFrame()
            self.ui.label_11.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
    # Диалоговое окно подтверждения перезаписи файла с данными
    def YesNoRewrite(self, btn):
        if btn.text() == "&Yes":
            # Сбор данных заново
            try:
                with main_connection.cursor() as cursor:
                    query = f"SELECT kp_id from users_upd WHERE users_upd.login = '{self.personal_id}'"
                    cursor.execute(query)
                    kp_id = cursor.fetchone()['kp_id']
                    result_link = parser(kp_id)
                    with open(result_link, "r", encoding="utf-8",
                              newline='') as file:
                        self.user_frame = pd.read_csv(result_link,sep=",")
                        self.reserved_full_frame = self.full_frame.copy()
                        self.full_frame = pd.merge(self.user_frame.drop(["year"], axis=1, inplace=False),
                                                   self.normalized_frame, how='inner', on='KP_id')
                        self.not_normalized_full_frame = pd.merge(self.user_frame.drop(["year"], axis=1, inplace=False),
                                                                  self.not_normalized_frame, how='inner', on='KP_id')
                        a_pen = csv.reader(file)
                        count = 0
                        for i in a_pen:
                            count += 1
                            if count == 1:
                                self.ui.textEdit.setText("Id фильма | Название фильма | Оценка фильма" + "\n")
                                continue
                            else:
                                buf = self.ui.textEdit.toPlainText() + "\n"
                                self.ui.textEdit.setText(buf + f"{i[0]} | {i[1]} | {i[2]}")

                    self.draw_user_hist()
            except:
                Connect_error_proc()

        elif btn.text() == "&No":
            # Использование уже скачанного ранее файла
            with open(f'Users/User_{self.personal_id}/KP_{self.personal_id}.csv', "r", encoding="utf-8", newline='') as file:
                self.user_frame = pd.read_csv(f'Users/User_{self.personal_id}/KP_{self.personal_id}.csv', sep = ",")
                a_pen = csv.reader(file)
                count = 0
                for i in a_pen:
                    count += 1
                    if count == 1:
                        self.ui.textEdit.setText("Id фильма | Название фильма | Оценка фильма" + "\n")
                        continue
                    else:
                        buf = self.ui.textEdit.toPlainText() + "\n"
                        self.ui.textEdit.setText(buf + f"{i[0]} | {i[1]} | {i[2]}")
            self.full_frame = pd.merge(self.user_frame, self.normalized_frame, how='inner', on='KP_id')
            self.not_normalized_full_frame = pd.merge(self.user_frame, self.not_normalized_frame, how='inner', on='KP_id')
            # Создание и отображение графиков
            self.draw_user_hist()

            # Выставить количество фильмов
            self.ui.pushButton_62.setText(str(self.user_frame.shape[0]))
            return 1
        else:
            self.ui.radioButton_13.setChecked(False)
            self.ui.textEdit.setText('')
            self.user_frame = pd.DataFrame()
            self.full_frame = pd.DataFrame()
            self.not_normalized_full_frame = pd.DataFrame()
            self.ui.label_11.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
   # Создать гистограмму оценок пользователя
    def draw_user_hist(self):
        self.user_frame.vote.hist(bins=100)
        plt.xlabel('Оценки пользователя')
        plt.ylabel('Количество оценок')
        plt.savefig(f"Users/User_{self.personal_id}/hist_vote.png", dpi=70)
        self.ui.label_143.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/hist_vote.png"))
        plt.close()

    # Использовать оценки базу данных для загрузки информации о пользователе
    def use_db(self):
        if self.ui.radioButton_10.isChecked():
            self.ui.label_148.setStyleSheet("border-bottom: 2px solid black;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_10.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.label_11.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')
            self.ui.radioButton_11.setChecked(False)
            self.ui.radioButton_13.setChecked(False)
            # Загрузить информацию из бд
            try:
                with main_connection.cursor() as cursor:
                    user_list_query = f"SELECT * FROM user_library WHERE user_library.login ='{self.personal_id}' AND WatchList = 0"
                    cursor.execute(user_list_query)
                    rows = cursor.fetchall()
                    if len(rows) == 0:
                        self.ui.textEdit.setText('Фильмы еще не добавлены в базу данных.')
                    else:
                        self.user_frame = pd.DataFrame(columns=['KP_id','film_name','vote'])
                        for i in rows:
                            self.user_frame = self.user_frame.append({'KP_id':i['Film_id'],"film_name":'-',"vote":i['vote']},ignore_index=True)
                        self.full_frame = pd.merge(self.user_frame, self.normalized_frame, how='inner', on='KP_id')
                        self.not_normalized_full_frame = pd.merge(self.user_frame, self.not_normalized_frame, how='inner',
                                                                  on='KP_id')
            except:
                Disconnect()
            self.reserved_full_frame = self.full_frame.copy()
        else:
            self.ui.textEdit.setText('')
            self.user_frame = pd.DataFrame()
            self.full_frame = pd.DataFrame()
            self.not_normalized_full_frame = pd.DataFrame()
            self.ui.label_148.setStyleSheet("border-bottom: initial;"
                                            'font: 75 13pt "Arial";')

    # Загрузить информацию об оцененных пользователем фильмах в базу данных
    def load_user_info_to_db(self):
        with main_connection.cursor() as cursor:
            fname = QFileDialog.getOpenFileName(self, "Open File", "C:\\Users\\Home PC\\Desktop\\Python",
                                                "CSV Files (*.csv)")
            if fname != ('', ''):
                # Очистить бд
                delete_query = f"DELETE FROM `user_library` WHERE login = '{self.personal_id}' AND Film_id > 0  AND WatchList = 0"
                cursor.execute(delete_query)
                main_connection.commit()
                try:
                    with open(fname[0], "r", encoding="utf-8", newline='') as file:
                        self.user_frame = pd.read_csv(fname[0], sep=",")
                        a_pen = csv.reader(file)
                        count = 0
                        for i in a_pen:
                            count += 1
                            if count == 1:
                                continue
                            # Проверка есть ли такой фильм в фильмотеке
                            if self.not_normalized_frame[self.not_normalized_frame['KP_id'] == int(i[0])].empty:
                                # Если такого фильма нет в фильмотеке
                                continue
                            Check_film_query = f"SELECT EXISTS(SELECT * FROM films WHERE Film_id ={i[0]})"
                            cursor.execute(Check_film_query)
                            if not cursor.fetchone()[
                                f'EXISTS(SELECT * FROM films WHERE Film_id ={i[0]})']:
                                # Если фильма нет, то нужно добавить
                                add_film_query = f"INSERT INTO `films`(Film_id,Film_name,Year) values ({i[0]},'{i[1]}',{int(i[3])});"
                                cursor.execute(add_film_query)
                                main_connection.commit()
                            # Связать фильм с пользоваталем
                            add_user_film_query = f"INSERT INTO `user_library`(login,Film_id,vote,WatchList) values ('{self.personal_id}',{i[0]},{i[2]},0);"
                            cursor.execute(add_user_film_query)
                            main_connection.commit()
                except Exception as Ex:
                    Disconnect()

                # Нарисовать гитсограмму
                self.draw_user_hist()

    # Вывод информации об оцененных пользователем фильмах из базы данных
    def show_user_info_from_db(self):
        try:
            with main_connection.cursor() as cursor:
                # Показать id список "Желаемого" для конкретного пользователя
                user_list_query = f"SELECT * FROM user_library  LEFT JOIN films ON (films.Film_id=user_library.Film_id) WHERE user_library.login ='{self.personal_id}' AND WatchList = 0"
                cursor.execute(user_list_query)
                rows = cursor.fetchall()
                count = 0
                self.ui.textEdit.setText('Фильмы пользователя:' + '\n' + '\n' + 'Название | Год выхода | Оценка' + '\n')
                if len(rows) == 0:
                    self.ui.textEdit.setText('Фильмы не добавлены в базу данных.')
                else:
                    for i in rows:
                        count += 1
                        name = i['Film_name']
                        buf = self.ui.textEdit.toPlainText()
                        self.ui.textEdit.setText(buf + f"{name}  ({i['Year']})  | {i['vote']}" + '\n')
                    main_connection.commit()

        except:
            Connect_error_proc()

    # Удалить все фильмы из списка "Смотреть позже пользователя"
    def clean_watch_list(self):
        try:
            with main_connection.cursor() as cursor:
                # Удалить все данные о желаниях пользователя
                delete_query = f"DELETE FROM `user_library` WHERE login = '{self.personal_id}' AND Film_id > 0 AND WatchList=1"
                cursor.execute(delete_query)
                main_connection.commit()
                self.ui.textEdit.setText('')
                self.ui.pushButton_65.setText('0')

        except:
            Connect_error_proc()

   # Показать содержимое списка "Смотреть позже"
    def show_watch_list(self):
        try:
            with main_connection.cursor() as cursor:
                # Показать id список "Желаемого" для конкретного пользователя
                user_list_query = f"SELECT * FROM user_library LEFT JOIN films ON (films.Film_id=user_library.Film_id) WHERE login ='{self.personal_id}' AND WatchList=1"
                cursor.execute(user_list_query)
                rows = cursor.fetchall()
                count = 0
                self.ui.textEdit.setText('Список "Смотреть позже":' + '\n')
                if len(rows) == 0:
                    self.ui.textEdit.setText('Список "Смотреть позже" пока что пуст.')
                else:
                    for i in rows:
                        count += 1
                        buf = self.ui.textEdit.toPlainText()
                        self.ui.textEdit.setText(buf + f"{i['Film_name']}  ({i['Year']})" + '\n')
        except:
            Disconnect()
            return

    # Добавить фильм в список "Смотреть позже"
    def add_to_watch(self):
        self.ui.pushButton_67.setStyleSheet("background-color: rgb(0, 170, 0);")
        self.ui.pushButton_67.setEnabled(False)
        try:
            with main_connection.cursor() as cursor:
                # Проверка есть ли такой фильм уже в таблице с фильмами
                Check_film_query =  f"SELECT EXISTS(SELECT * FROM films WHERE films.Film_id ={self.predictable_film})"
                cursor.execute(Check_film_query)
                if not cursor.fetchone()[f'EXISTS(SELECT * FROM films WHERE films.Film_id ={self.predictable_film})']:
                    add_film_query = f"INSERT INTO `films`(Film_id, Film_name, Year) values ({self.predictable_film},'{self.not_normalized_frame[self.not_normalized_frame['KP_id'] == self.predictable_film].iloc[0].title}',{int(self.not_normalized_frame[self.not_normalized_frame['KP_id'] == self.predictable_film].iloc[0].year)});"
                    cursor.execute(add_film_query)
                    main_connection.commit()
                add_user_film_query = f"INSERT INTO `user_library`(login,Film_id,WatchList) values ('{self.personal_id}',{self.predictable_film},1);"
                cursor.execute(add_user_film_query)
                main_connection.commit()
                self.ui.pushButton_67.setStyleSheet("background-color: rgb(0, 200, 0);")
                self.ui.pushButton_67.setEnabled(False)
                self.ui.pushButton_66.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.ui.pushButton_66.setEnabled(True)
                self.ui.pushButton_65.setText(str(int(self.ui.pushButton_65.text()) + 1))
        except:
            Disconnect()

    # Удалить фильм из списка "Смотреть позже"
    def delete_from_watch(self):
        try:
            with main_connection.cursor() as cursor:
                # получить id фильма по таблице
                delete_query = f"DELETE FROM `user_library` WHERE Film_id = {self.predictable_film} AND login = '{self.personal_id}' AND WatchList=1"
                cursor.execute(delete_query)
                main_connection.commit()
                self.ui.pushButton_67.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.ui.pushButton_67.setEnabled(True)
                self.ui.pushButton_66.setStyleSheet("background-color: rgb(200, 0, 0);")
                self.ui.pushButton_66.setEnabled(False)
                self.ui.pushButton_65.setText(str(int(self.ui.pushButton_65.text()) - 1))
        except:
            Connect_error_proc()

    # Сменить отображаемое имя пользователя
    def change_name(self):
        # Проверка корректности
        if  3 <= len(self.ui.lineEdit_10.text()) < 16:
            try:
                with main_connection.cursor() as cursor:
                    change_name_query = f"UPDATE `users_upd` SET users_upd.name='{self.ui.lineEdit_10.text()}'  WHERE users_upd.login = '{self.personal_id}'"
                    cursor.execute(change_name_query)
                    main_connection.commit()
                    self.ui.label_4.setText('Nickname: ' + self.ui.lineEdit_10.text())
                self.ui.lineEdit_10.setText('')
            except:
                Connect_error_proc()
        else:
            Error_1('Недопустимое значение.\nДлина имени должна быть от 3 до 16 символов.')


    # Изменить пароль от аккаунта
    def change_password(self):
        # Проверка корректности пароля
        import re
        st = self.ui.lineEdit_11.text()
        pattern = r"([a-zA-Z\d]+)"
        res = re.search(pattern, st)
        if not (res is None) and (res.group(1) == st) and (len(self.ui.lineEdit_11.text()) > 7):
            if self.ui.lineEdit_11.text() != self.ui.lineEdit_13.text():
                Error_1('Ошибка.\nПароли не совпадают.')
            else:
                confirmation = QMessageBox()
                confirmation.setWindowTitle('Уведомление')
                confirmation.setText('Вы уверены, что хотите сменить пароль?')
                confirmation.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
                confirmation.buttonClicked.connect(self.YesNoPassword)
                confirmation.exec_()
        else:
            Error_1('Неподходяший пароль.\nПароль должен состоять из цифр и английских букв.\nКоличество символов не менее 7.')

    # Диалоговое окно с подтверждением изменения пароля
    def YesNoPassword(self,btn):
        # Подтверждение
        try:
            with main_connection.cursor() as cursor:
                if btn.text() == "OK":
                    change_password_query = f"UPDATE `users_upd` SET users_upd.password='{self.ui.lineEdit_11.text()}'  WHERE users_upd.login = '{self.personal_id}'"
                    cursor.execute(change_password_query)
                    main_connection.commit()
                else:
                    QtWidgets.QMessageBox.about(self, "Уведомление", "Отмена изменений")
                self.ui.lineEdit_11.setText('')
                self.ui.lineEdit_13.setText('')
        except:
            Connect_error_proc()

    # Добавить идентификатор сервиса "Кинопоиск"
    def add_kp_id(self):
        if (len(self.ui.lineEdit_15.text()) == 8) and (self.ui.lineEdit_15.text().isdigit()):
            try:
                with main_connection.cursor() as cursor:
                    # Проверка, есть ли уже такой login
                    add_kp_id_query = f"UPDATE `users_upd` SET users_upd.kp_id={self.ui.lineEdit_15.text()}  WHERE users_upd.login = '{self.personal_id}'"
                    cursor.execute(add_kp_id_query)
                    main_connection.commit()
                    self.ui.label_3.setText(f'ID: {self.ui.lineEdit_15.text()}')
            except:
                Connect_error_proc()
        else:
            Error_1('Ошибка.\nПожалуйста, укажите корректный id Кинопоиска')

    # Изменить почту
    def change_email(self):
        # Проверка корректности почты
        import re
        st = self.ui.lineEdit_12.text()
        pattern = r"([a-zA-Z\d._]+@[a-z]+.[a-z]+)"
        res = re.search(pattern, st)
        if not (res is None) and (res.group(1) == st):
            confirmation = QMessageBox()
            confirmation.setWindowTitle('Уведомление')
            confirmation.setText('Вы уверены, что хотите сменить почту?')
            confirmation.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
            confirmation.buttonClicked.connect(self.YesNoEmail)
            confirmation.exec_()
        else:
            Error_1('Некорректная почта.\nПочта должна быть следующиего вида:\nexample@gmail.com')

    # Диалоговое окно с подтверждением изменения почты
    def YesNoEmail(self,btn):
        try:
            with main_connection.cursor() as cursor:
                if btn.text() == "OK":
                    change_email_query = f"UPDATE `users_upd` SET users_upd.email='{self.ui.lineEdit_12.text()}'  WHERE users_upd.login = '{self.personal_id}'"
                    cursor.execute(change_email_query)
                    main_connection.commit()
                else:
                    QtWidgets.QMessageBox.about(self, "Уведомление",
                                                "Отмена изменений")
                self.ui.lineEdit_12.setText('')
        except:
            Connect_error_proc()

    # Изменить фотографию
    def change_photo(self):
        confirmation = QMessageBox()
        confirmation.setWindowTitle('Уведомление')
        confirmation.setText('Вы уверены, что хотите сменить фотографию?')
        confirmation.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
        confirmation.buttonClicked.connect(self.YesNoPhoto)
        confirmation.exec_()

    # Диалоговое окно с подтверждением изменения фотографии
    def YesNoPhoto(self,btn):
        try:
            with main_connection.cursor() as cursor:
                if btn.text() == "OK":
                    # Изменение аватарки
                    fname = QFileDialog.getOpenFileName(self, "Open File", "C:\\Users\\Home PC\\Desktop\\Python", "JPG Files (*.jpg);;PNG Files (*.png)")
                    if fname:
                        # Загрузить в бд
                        with open(fname[0], 'rb') as file:
                            BinaryData = file.read()
                        query = f"UPDATE `users_upd` SET users_upd.photo= %s  WHERE users_upd.login = '{self.personal_id}'"
                        cursor.execute(query, (BinaryData,))
                        main_connection.commit()
                    # Удалить файл со старым фото с ПК
                    # Вызов функции, чтобы обновить отображение картинки
                    with open(f"Users/User_{self.personal_id}/Profile_photo.png", 'wb') as file:
                        file.write(BinaryData)
                    modify_photo(f"Users/User_{self.personal_id}/Profile_photo.png")
                    self.ui.label_7.setPixmap(QtGui.QPixmap(f"Users/User_{self.personal_id}/Profile_photo_upd.png"))
                else:
                    QtWidgets.QMessageBox.about(self, "Уведомление",
                                                "Отмена изменений")
        except:
            Connect_error_proc()

    # Выбора способа кластеризации для определения сфер интересов
    def make_clustering(self):
        if self.ui.radioButton_7.isChecked():
            self.define_user_interests("K_Means")
        elif self.ui.radioButton_8.isChecked():
            self.define_user_interests("Hierarchical")
        elif self.ui.radioButton_9.isChecked():
            self.define_user_interests("DBSCAN")
        else:
            Error_1('Ошибка.\nВыберите алгоритм кластеризации.')

    # Вызов виджета для изменения используемых признаков
    @pyqtSlot(int)
    def show_features_menu(self):
        feat_wnd = Features_window(parent=self)
        feat_wnd.signal.connect(self.result_features)
        feat_wnd.show()

    # Обработка результатов выбранных признаков и изменение набора данных
    @pyqtSlot(list)
    def result_features(self, lst):
        if not self.full_frame.empty:
            try:
                self.normalized_frame = self.reserved_normalized_frame.copy()
                self.full_frame = self.reserved_full_frame.copy()
                genres = pd.DataFrame()
                countries = pd.DataFrame()
                if 'Жанры' in lst:
                    genres = self.normalized_frame.iloc[:,191:217]
                    lst.remove('Жанры')
                if 'Страны' in lst:
                    countries = self.normalized_frame.iloc[:,14:191]
                    lst.remove('Страны')
                eqvl = {'Год выхода':'year',"Средняя оценка на Кинопоиске":'rating_kinopoisk','Количество оценок на Кинопоиске':'kinopoisk_votes',
                        "Средняя оценка на IMDb":'imDbRating', 'Количество оценок на IMDb':'imDbRatingVotes', 'Оценка критиков': 'CriticsVote',
                        'Количество оценок критиков':'Critics_votes_amount','Продолжительность':'runtimeMins','Количество премий Оскар':'oscar_win_count',
                        'Количество номинаций на Оскар':'oscar_nominee_count','Количество других премий':'other_win_count',
                        'Количество других номинаций':'other_nominee_count','Входит в ТОП250 IMDB':'isTopRated','Десятилетие выхода':'release_decade'}
                lst_2 = list(map(lambda x:eqvl[x],lst))
                frames_norm = [self.normalized_frame['KP_id'],self.normalized_frame[lst_2],]
                frames_full = [self.full_frame['KP_id'],self.full_frame[lst_2],]
                if not genres.empty:
                    frames_norm.append(genres)
                    frames_full.append(genres)
                if not countries.empty:
                    frames_norm.append(countries)
                    frames_full.append(countries)

                result_1 = pd.concat(frames_norm, axis=1)
                result_2 = pd.concat(frames_full, axis=1)
                buf = self.full_frame
                self.full_frame = result_2
                self.full_frame["film_name"] = buf["film_name"]
                self.full_frame["vote"] = buf["vote"]
                self.normalized_frame = result_1
                count = 0
                for i in lst:
                    count += 1
                    if count == 1:
                        self.ui.textEdit_5.setText(f"1. {i}")
                        self.ui.textEdit_3.setText(f"1. {i}")
                        self.ui.textEdit_7.setText(f"1. {i}")
                        self.ui.textEdit_17.setText(f"1. {i}")
                    else:
                        buf = self.ui.textEdit_5.toPlainText() + "\n"
                        self.ui.textEdit_5.setText(buf + f"{count}. " + i)
                        self.ui.textEdit_3.setText(buf + f"{count}. " + i)
                        self.ui.textEdit_7.setText(buf + f"{count}. " + i)
                        self.ui.textEdit_17.setText(buf + f"{count}. " + i)
                if not genres.empty:
                    self.ui.textEdit_5.setText(self.ui.textEdit_5.toPlainText() + '\n'+ f"{count + 1}. " + 'Жанры')
                    self.ui.textEdit_3.setText(self.ui.textEdit_3.toPlainText() + '\n'+ f"{count + 1}. " + 'Жанры')
                    self.ui.textEdit_7.setText(self.ui.textEdit_7.toPlainText() + '\n'+ f"{count + 1}. " + 'Жанры')
                    self.ui.textEdit_17.setText(self.ui.textEdit_17.toPlainText() + '\n'+ f"{count + 1}. " + 'Жанры')
                if not countries.empty:
                    self.ui.textEdit_5.setText(self.ui.textEdit_5.toPlainText() + '\n'+ f"{count + 2}. " + 'Страны')
                    self.ui.textEdit_3.setText(self.ui.textEdit_3.toPlainText() + '\n'+ f"{count + 2}. " + 'Страны')
                    self.ui.textEdit_7.setText(self.ui.textEdit_7.toPlainText() + '\n'+ f"{count + 2}. " + 'Страны')
                    self.ui.textEdit_17.setText(self.ui.textEdit_17.toPlainText() + '\n'+ f"{count + 2}. " + 'Страны')

            except Exception as Ex:
                pass
        else:
            Error_1('Ошибка.\nПожалуйста, загрузите данные о пользователе')

    # Построить график распределения данных пользователя
    def show_user_chart(self):
        if self.user_frame.empty:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
        else:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2)
            pca.fit(self.full_frame.drop(["KP_id","film_name","vote"], axis=1, inplace=False))
            pca_data = pca.transform(self.full_frame.drop(["KP_id","film_name","vote"], axis=1, inplace=False))
            plt.figure(figsize=(10, 7))
            plt.scatter(pca_data[:, 0], pca_data[:, 1])
            plt.show()

    # Выбор алгоритма KNN для обучения модели прогнозирования
    def select_KNN(self):
        if not self.user_frame.empty:
            self.ui.radioButton_2.setChecked(False)
            self.ui.radioButton_3.setChecked(False)
            self.ui.radioButton_12.setChecked(False)

            # Выгрузка из базы данных метода и сохранение в активном методе
            import ast
            try:
                with main_connection.cursor() as cursor:
                    query = f"SELECT users_upd.knn_method FROM users_upd WHERE login = '{self.personal_id}'"
                    cursor.execute(query)
                    #main_connection.commit()
                    rez = cursor.fetchone()['knn_method']
                    if rez is None:
                        Error_1('Ошибка.\nДля данного алгоритма еще не сохранены\nоптимальные параметры.')
                    else:
                        rez = ast.literal_eval(rez)
                        frame_train, frame_test, answer_train, answer_test = train_test_split(
                            self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                            self.full_frame["vote"], test_size=self.frame_separator)
                        self.using_regression_method = KNeighborsRegressor(n_neighbors=int(rez['n_neighbors']), weights=rez['weights'],
                                                      p=int(rez['p']))

                        self.using_regression_method.fit(frame_train, answer_train)
                        rez = self.using_regression_method.predict(frame_test)
            except:
                Connect_error_proc()
        else:
            self.ui.radioButton.setChecked(False)
            Error_1('Ошибка.\nПожалуйста, загрузите информацию о фильмах.')

    # Выбор алгоритма Linear regression для обучения модели прогнозирования
    def select_linear_regression(self):
        self.ui.radioButton_12.setChecked(False)
        self.ui.radioButton_3.setChecked(False)
        self.ui.radioButton.setChecked(False)
        if not self.user_frame.empty:
            # Выгрузка из базы данных метода и сохранение в активном методе
            import ast
            try:
                with main_connection.cursor() as cursor:
                    query = f"SELECT users_upd.lr_method FROM users_upd WHERE login = '{self.personal_id}'"
                    cursor.execute(query)
                    main_connection.commit()
                    rez = cursor.fetchone()['lr_method']
                    if rez is None:
                        Error_1('Ошибка.\nДля данного алгоритма еще не сохранены\nоптимальные параметры.')
                    else:
                        rez = ast.literal_eval(rez)

                        frame_train, frame_test, answer_train, answer_test = train_test_split(
                            self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                            self.full_frame["vote"], test_size=self.frame_separator)

                        if rez['type'] == 'standart':
                            self.using_regression_method = LinearRegression()
                        if rez['type'] == 'Ridge':
                            self.using_regression_method = Ridge(alpha=rez['alpha'])
                        if rez['type'] == 'Lasso':
                            self.using_regression_method = Lasso(alpha=rez['alpha'])

                        self.using_regression_method.fit(frame_train, answer_train)
                        rez = self.using_regression_method.predict(frame_test)
            except:
                Connect_error_proc()
        else:
            self.ui.radioButton_2.setChecked(False)
            Error_1('Ошибка.\nПожалуйста, загрузите информацию о фильмах.')

    # Выбор алгоритма Gradient descent для обучения модели прогнозирования
    def select_gradient_descent(self):
        if not self.user_frame.empty:
            self.ui.radioButton.setChecked(False)
            self.ui.radioButton_2.setChecked(False)
            self.ui.radioButton_12.setChecked(False)

            # Выгрузка из базы данных метода и сохранение в активном методе
            import ast
            try:
                with main_connection.cursor() as cursor:
                    query = f"SELECT users_upd.gd_method FROM users_upd WHERE login = '{self.personal_id}'"
                    cursor.execute(query)
                    main_connection.commit()
                    rez = cursor.fetchone()['gd_method']
                    if rez is None:
                        Error_1('Ошибка.\nДля данного алгоритма еще не сохранены\nоптимальные параметры.')
                    else:
                        rez = ast.literal_eval(rez)
                        X_train, X_test, y_train, y_test = train_test_split(
                            self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                            self.full_frame["vote"], test_size=self.frame_separator)

                        self.using_regression_method = SGDRegressor(tol=rez['tol'], alpha=rez['alpha'], max_iter=rez['max_iter'])
                        self.using_regression_method.fit(X_train, y_train)
                        rez = self.using_regression_method.predict(X_test)
            except:
                Connect_error_proc()
        else:
            self.ui.radioButton_3.setChecked(False)
            Error_1('Ошибка.\nПожалуйста, загрузите информацию о фильмах.')

    # Выбор алгоритма Random forest для обучения модели прогнозирования
    def select_random_forest(self):
        if not self.user_frame.empty:
            self.ui.radioButton_2.setChecked(False)
            self.ui.radioButton_3.setChecked(False)
            self.ui.radioButton.setChecked(False)

            import ast
            try:
                with main_connection.cursor() as cursor:
                    query = f"SELECT users_upd.rf_method FROM users_upd WHERE login = '{self.personal_id}'"
                    cursor.execute(query)
                    main_connection.commit()
                    rez = cursor.fetchone()['rf_method']
                    if rez is None:
                        Error_1('Ошибка.\nДля данного алгоритма еще не сохранены\nоптимальные параметры.')
                    else:
                        rez = ast.literal_eval(rez)
                        frame_train, frame_test, answer_train, answer_test = train_test_split(
                            self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False), self.full_frame["vote"],
                            test_size=self.frame_separator)

                        self.using_regression_method = RandomForestRegressor(n_estimators=int(rez['n_estimators']), max_features=float(rez['max_features']))
                        self.using_regression_method.fit(frame_train, answer_train)
                        rez = self.using_regression_method.predict(frame_test)
            except:
                Connect_error_proc()
        else:
            self.ui.radioButton_12.setChecked(False)
            Error_1('Ошибка.\nПожалуйста, загрузите информацию о фильмах.')

    # Сделать активной кнопку K-Means
    def select_KMeans(self):
        self.ui.radioButton_8.setChecked(False)
        self.ui.radioButton_9.setChecked(False)

    # Сделать активной кнопку hierarchical
    def select_hieararchical(self):
        self.ui.radioButton_7.setChecked(False)
        self.ui.radioButton_9.setChecked(False)

    # Сделать активной кнопку DBSCAN
    def select_DBSCAN(self):
        self.ui.radioButton_7.setChecked(False)
        self.ui.radioButton_8.setChecked(False)


    # Перход в меню графиков
    def pass_to_statistics(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.stackedWidget_2.setCurrentIndex(0)

    # Прогнозирование оценки
    def predict_vote(self):
        if self.user_frame.empty:
            Error_1('Ошибка.\nПожалуйста, загрузите информацию о фильмах')
            return
        else:
            if not ((self.ui.radioButton.isChecked()) or (self.ui.radioButton_2.isChecked()) or (self.ui.radioButton_3.isChecked()) or (self.ui.radioButton_12.isChecked())):
                Error_1('Ошибка.\nПожалуйста, выберите метод прогнозирования')
            else:
                if self.using_regression_method == "":
                    Error_1('Ошибка.\nМодель не обучена для данного алгоритма.')
                else:
                    # Нужно взять фильм
                    rez_2 = self.normalized_frame[self.normalized_frame['KP_id']==self.predictable_film].drop(["KP_id"], axis=1, inplace=False)
                    for i in rez_2.columns:
                        print(i)
                    try:
                        predict = self.using_regression_method.predict(rez_2)
                    except Exception as EX:
                        print(EX)

                    # Оформление
                    self.ui.label_118.setText(f"Уровень заинтересованности: {round(predict[0],3)}")

                    round_system = {'1': (0, 1.5), '2': (1.5, 2.6), '3': (2.6, 3.6), '4': (3.6, 4.6), '5': (4.6, 5.6),
                                    '6': (5.6, 6.6), '7': (6.6, 7.6), '8': (7.6, 8.6), '9': (8.6, 9.6), '10': (9.6, 10)}
                    # Округленная оценка
                    if round_system[str(predict[0])[0]][0] < predict[0] <= round_system[str(predict[0])[0]][1]:
                        final_vote = str(predict[0])[0]
                        self.ui.label_119.setText(f"Вероятная оценка: {str(predict[0])[0]}")
                    else:
                        final_vote = str(int(str(predict[0])[0]) + 1)
                        self.ui.label_119.setText(f"Вероятная оценка: {int(str(predict[0])[0]) + 1}")
                    comments = {'1': 'Фильм совершенно Вам не подходит. Советуем воздержаться от просмотра и выбрать что-то получше.',
                                '2': 'Фильм совершенно Вам не подходит. Советуем воздержаться от просмотра и выбрать что-то получше.',
                                '3': 'Фильм совершенно Вам не подходит. Советуем воздержаться от просмотра и выбрать что-то получше.',
                                '4': 'Фильм совершенно Вам не подходит. Советуем воздержаться от просмотра и выбрать что-то получше.',
                                '5': 'Фильм среднего уровня. Может как приятно удивить, так и сильно разочаровать. Рекомендуем смотреть на свой страх и риск. :)',
                                '6': 'Фильм среднего уровня. Может как приятно удивить, так и сильно разочаровать. Рекомендуем смотреть на свой страх и риск. :)',
                                '7': 'Хороший вариант для просмотра. В вашей фильмотеке есть много похожих фильмов. Уверены, Вы не разочаруетесь.',
                                '8': 'Хороший вариант для просмотра. В вашей фильмотеке есть много похожих фильмов. Уверены, Вы не разочаруетесь.',
                                '9': 'Замечательный вариант для просмотра. Фильм соответствует Вашим вкусам. Рекомендуем к просмотру в первую очередь.',
                                '10': 'Замечательный вариант для просмотра. Фильм соответствует Вашим вкусам. Рекомендуем к просмотру в первую очередь.'}
                    self.ui.label_124.setText(comments[final_vote])
                    if int(final_vote) > 7:
                        self.ui.label_117.setStyleSheet("background-color:rgb(0, 175, 0);\n"
                                                        "font: 75 15pt \"Arial\";\n"
                                                        "color: rgb(255, 255, 255);"
                                                        "border-bottom-left-radius:0;"
                                                        "border-bottom-RIGHT-radius:0;")
                        self.ui.label_117.setText('Высокая заинтересованность')
                        self.ui.label_113.setPixmap(QtGui.QPixmap("Pics/like.png"))
                    elif int(final_vote) > 4:
                        self.ui.label_113.setPixmap(
                            QtGui.QPixmap("Pics/question.png"))
                        self.ui.label_117.setText('Средняя заинтересованность')
                        self.ui.label_117.setStyleSheet("background-color:rgb(181, 181, 181);\n"
                                                        "font: 75 15pt \"Arial\";\n"
                                                        "color: rgb(255, 255, 255);"
                                                        "border-bottom-left-radius:0;"
                                                        "border-bottom-RIGHT-radius:0;")
                    else:
                        self.ui.label_113.setPixmap(
                            QtGui.QPixmap("Pics/dislike.png"))
                        self.ui.label_117.setStyleSheet("background-color:rgb(255,0,0);\n"
                                                        "font: 75 15pt \"Arial\";\n"
                                                        "color: rgb(255, 255, 255);"
                                                        "border-bottom-left-radius:0;"
                                                        "border-bottom-RIGHT-radius:0;")
                        self.ui.label_117.setText('Низкая заинтересованность')

    # Уведомление о количестве используемых фильмов для обучения модели
    def call_QMB(self):
        # 3 ситуации: x<100 - красная зона
        # 100<x<200 - желтая зона
        # 200<x - зеленая зона
        frame_status = QMessageBox()
        if int(self.ui.pushButton_62.text())<300:
            frame_status.setWindowTitle('Мало фильмов для обучения.')
            frame_status.setIcon(QMessageBox.Warning)
            frame_status.setText('Малое количество')
            frame_status.setInformativeText(f"Количество фильмов: {self.ui.pushButton_62.text()}. Для улучшение качества прогнозов добавьте больше фильмов")
            frame_status.setStandardButtons(QMessageBox.Ok)
        if 300<=int(self.ui.pushButton_62.text())<550:
            frame_status.setWindowTitle('Среднее количество фильмов для обучения.')
            frame_status.setIcon(QMessageBox.Warning)
            frame_status.setText('Среднее количество')
            frame_status.setInformativeText(f"Количество фильмов: {self.ui.pushButton_62.text()}. Для улучшение качества прогнозов добавьте больше фильмов")
            frame_status.setStandardButtons(QMessageBox.Ok)
        if int(self.ui.pushButton_62.text())>=550:
            frame_status.setWindowTitle('Большое число фильмов для обучения.')
            frame_status.setIcon(QMessageBox.Warning)
            frame_status.setText('Много фильмов')
            frame_status.setInformativeText(f"Количество фильмов: {self.ui.pushButton_62.text()}. Такое значение оптимально подходит для прогнозирования")
            frame_status.setStandardButtons(QMessageBox.Ok)
        frame_status.exec_()

    # Уведомление о количестве фильмов в списке "Смотреть позже"
    def call_QMB_2(self):
            frame_status = QMessageBox()
            frame_status.setWindowTitle('Уведомление')
            frame_status.setIcon(QMessageBox.Warning)
            frame_status.setText('Список "Смотреть позже"')
            frame_status.setInformativeText(f'Количество фильмов в списке "Смотреть позже": {self.ui.pushButton_65.text()}')
            frame_status.setStandardButtons(QMessageBox.Ok)
            frame_status.exec_()

    # График изменения средней оценки пользователя для разных жанров
    def Vote_by_genres(self):
        if not self.user_frame.empty:
            buf_frame =  self.not_normalized_full_frame[['genres', 'vote']]
            buf_frame['genres'] = buf_frame['genres'].apply(
                lambda x: list(map(lambda y: y.strip()[1:-1], x[1:-1].split(","))))
            buf_genres_list = list()
            for i in buf_frame.genres:
                buf_genres_list.extend(i)
            buf_genres_list = list(map(lambda x: x.capitalize(), buf_genres_list))
            buf_genres_list = list(set(list(map(lambda x: (buf_genres_list.count(x), x), buf_genres_list))))
            buf_genres_list.sort(reverse=True)
            vote_rate = list()
            for i in buf_genres_list:
                vote_rate.append(round(buf_frame[buf_frame['genres'].apply(
                    lambda x: 1 if (i[1] in x) or (i[1].lower() in x) else 0) == 1].vote.mean(), 3))
            buf_genres_list = list(map(lambda x: f'{x[1]}: ({x[0]})', buf_genres_list))

            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            fig.set_figwidth(12)  # ширина и
            fig.set_figheight(8)  # высота "Figure"
            bar_plot = plt.barh(buf_genres_list, vote_rate)
            ax.set_title('Распределение по жанрам')
            ax.set_xlabel('Средняя оценка')

            def autolabel(rects):
                count = -1
                for idx, rect in enumerate(bar_plot):
                    count += 1
                    height = rect.get_height()
                    ax.text(1.03 * rect.get_width(), rect.get_y() + rect.get_height() / 2,
                            vote_rate[idx],
                            ha='center', va='center', rotation=0)
            autolabel(bar_plot)
            plt.savefig(f'Users/User_{self.personal_id}/vote_ny_genres.png',
                        bbox_inches='tight', transparent=True, dpi=90)

        self.ui.label_51.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/vote_ny_genres.png'))
        self.ui.stackedWidget_2.setCurrentIndex(1)

    # График разницы в оценках пользователяпо сравнению с сервисами «Кинопоиск», «IMDb» и кинокритиками.
    def Chart_1(self):
        try:
            if not self.user_frame.empty:
                self.ui.stackedWidget_2.setCurrentIndex(2)
                self.chart_1_counter += 1
                if self.chart_1_counter == 1:
                    chart_1 = Window_2(user_data=self.user_frame,film_data=self.not_normalized_frame)
                    chartview = QChartView(chart_1 .chart)
                    self.ui.gridLayout.addWidget(chartview)
            else:
                Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')
        except Exception as Ex:
            pass

    # График разницы в оценках пользователя при наличии наград или присутствии фильма в рейтинге ТОП 250
    def Chart_2(self):
        if not self.user_frame.empty:
            self.ui.stackedWidget_2.setCurrentIndex(3)
            self.chart_2_counter += 1
            if self.chart_2_counter == 1:
                window = Window_1(user_data=self.user_frame,film_data=self.not_normalized_frame)
                chartview = QChartView(window.chart)
                self.ui.gridLayout_8.addWidget(chartview)
        else:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')

    # График самых частых оценок при разном количестве премий Оскар
    def Chart_4(self):
        if not self.user_frame.empty:
            self.ui.stackedWidget_2.setCurrentIndex(4)
            self.chart_4_counter += 1
            if self.chart_4_counter == 1:
                chart_4 = Window_4(user_data=self.user_frame,film_data=self.not_normalized_frame)
                chartview_4 = QChartView(chart_4.chart)
                self.ui.gridLayout_5.addWidget(chartview_4)
        else:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')

    # График средних оценок для разных десятилейти
    def Chart_5(self):
        if not self.user_frame.empty:
            self.ui.stackedWidget_2.setCurrentIndex(5)
            self.chart_5_counter += 1
            if self.chart_5_counter == 1:
                chart_5 = Window_5(user_data=self.user_frame,film_data=self.not_normalized_frame)
                chartview_5 = QChartView(chart_5.chart)
                self.ui.gridLayout_7.addWidget(chartview_5)
        else:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')


    # График зависимости заинтересованности в просмотре от года выхода фильма
    def Chart_6(self):
        if not self.user_frame.empty:
            self.ui.stackedWidget_2.setCurrentIndex(6)
            self.chart_6_counter += 1
            if self.chart_6_counter == 1:
                chart_6 = Window_6(user_data=self.user_frame,film_data=self.not_normalized_frame)
                chartview_6 = QChartView(chart_6.chart)
                self.ui.gridLayout_6.addWidget(chartview_6)
        else:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')

    # График показателя оценивания популярных и непопулярных фильмов
    def Chart_7(self):
        if not self.user_frame.empty:
            self.ui.stackedWidget_2.setCurrentIndex(7)
            self.chart_7_counter += 1
            if self.chart_7_counter == 1:
                chart_7 = Window_7(user_data=self.user_frame,film_data=self.not_normalized_frame)
                chartview_7 = QChartView(chart_7.chart)
                self.ui.gridLayout_2.addWidget(chartview_7)
        else:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные')


    # Страница прогнозирования оценки
    def predict_vote_page(self):
        # Начальные параметры для поля прогноза
        self.ui.label_117.setStyleSheet('font: 75 15pt "Arial";'
                                       'color: rgb(255, 255, 255);'
                                       'background-color: rgb(85, 0, 127);'
                                       'border-top-left-radius: 10%;'
                                       'border-bottom-left-radius:0;'
                                       'border-bottom-RIGHT-radius:0;'
                                       '')
        self.ui.label_118.setText('')
        self.ui.label_124.setText('')
        self.ui.label_113.setPixmap(QtGui.QPixmap())
        self.ui.label_119.setText('Для прогнозирования вероятной оценки\nнажмите кнопку "Далее", рядом с названием\nфильма.')

        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget_3.setCurrentIndex(2)

        # Подробнее о фильме
        self.ui.pushButton_48.clicked.connect(lambda: self.More_info_film())

    # Перехол на старницу с полной информацией
    def More_info_film(self):                                                         # Здесь нужно сохранить id фильма
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget_3.setCurrentIndex(1)

    def foo1(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.stackedWidget_3.setCurrentIndex(3)


    # Процедура очистки экрана поиска
    def clean_layout(self, layout_name):
        full_len =layout_name.count()
        while layout_name.count()>0:
            full_len -= 1
            item = layout_name.takeAt(0)
            if full_len == 0:
                continue
            else:
                item.widget().deleteLater()

    # Определение схожести названий фильмов
    def fix_command(self,text, words):
        import numpy as np
        from fuzzywuzzy import fuzz
        res = fuzz.ratio(text,words)
        if res > 70:
            return text
        return

    # Вывод пользовательского виджета с описанием краткой информации об 1 фильме
    def out_film(self,result, film):
        wdgt = CoordWidget(result.iloc[film]['KP_id'])
        wdgt.execute.connect(self.execute_widget)  ## Тестовая фича !
        wdgt.ui.label_11.setText(result.iloc[film]['title'])
        wdgt.ui.label_3.setText("Год: "+str(int(result.iloc[film]['year'])))

        # Вывод стран
        count = 0
        for i in result.iloc[film]['countries']:
            count += 1
            if count == 1:
                wdgt.ui.label_4.setText("Страна: " + i)
            else:
                buf = wdgt.ui.label_4.text() + ', '
                wdgt.ui.label_4.setText(buf + i)

        # Вывод жанров
        count = 0
        for i in result.iloc[film]['genres']:
            count += 1
            if count == 1:
                wdgt.ui.label_5.setText("Жанр: " + i.lower())
            else:
                buf = wdgt.ui.label_5.text() + ', '
                wdgt.ui.label_5.setText(buf + i.lower())

        self.ui.found_films.addWidget(wdgt,0,QtCore.Qt.AlignTop)

        # Оценки
        wdgt.ui.label_7.setText(str(result.iloc[film]['rating_kinopoisk']))
        wdgt.ui.label_8.setText(str(result.iloc[film]['imDbRating']))
        # КП
        if 1000 <= int(result.iloc[film]['kinopoisk_votes']) < 1000000:
            wdgt.ui.label_2.setText(str(int(result.iloc[film]['kinopoisk_votes']))[:-3]+'K')
        elif int(result.iloc[film]['kinopoisk_votes']) >= 1000000:
            wdgt.ui.label_2.setText(str(int(result.iloc[film]['kinopoisk_votes']))[:-6] + 'M')
        else:
            wdgt.ui.label_2.setText(str(int(result.iloc[film]['kinopoisk_votes'])))

        # IMDB
        if 1000 <= int(result.iloc[film]['imDbRatingVotes']) < 1000000:
            wdgt.ui.label_10.setText(str(int(result.iloc[film]['imDbRatingVotes']))[:-3]+'K')
        elif int(result.iloc[film]['imDbRatingVotes']) >= 1000000:
            wdgt.ui.label_10.setText(str(int(result.iloc[film]['imDbRatingVotes']))[:-6]+'.'+str(int(result.iloc[film]['imDbRatingVotes']))[-5]+'M')
        else:
            wdgt.ui.label_10.setText(str(int(result.iloc[film]['imDbRatingVotes'])))

        # Картинка
        try:
            if not os.path.exists(f'Posters_2/{result.iloc[film]["KP_id"]}' + '.jpg'):
                response = requests.get(result.iloc[film]["poster"])
                img_option = open(f'Posters_2/{result.iloc[film]["KP_id"]}' + '.jpg', "wb")
                img_option.write(response.content)
                img_option.close()
            wdgt.ui.label.setPixmap(QtGui.QPixmap(f'Posters_2/{result.iloc[film]["KP_id"]}' + '.jpg'))
        except:
            wdgt.ui.label.setPixmap(QtGui.QPixmap(f'Posters_2/{result.iloc[film]["KP_id"]}' + '.jpg'))

    # Поиск фильма
    def search_button(self):
        if not self.ui.lineEdit.text() == "":
            if len(self.ui.lineEdit.text()) >= 2:
                self.clean_layout(self.ui.found_films) # Очистка от старых запросов
                request = self.ui.lineEdit.text().lower()
                result = self.not_normalized_frame[self.not_normalized_frame['lower_title'] == request]

                # 2 часть запроса
                bf_1 = self.not_normalized_frame[self.not_normalized_frame['lower_title'].apply(lambda x: 1 if self.fix_command(x,request) else 0 )==1]
                bf_2 = self.not_normalized_frame[self.not_normalized_frame['lower_title'].apply(lambda x: 1 if request in x else 0) == 1]
                rez_buf = pd.concat([bf_1, bf_2], axis=0)
                rez_buf = rez_buf.drop_duplicates()

                rez_buf = rez_buf[rez_buf["KP_id"].apply(lambda x: 1 if x in result.KP_id.values else 0) == 0]

                if result.empty and rez_buf.empty:
                    nothing_widget = Widget_2()
                    self.ui.found_films.addWidget(nothing_widget)
                    self.ui.stackedWidget.setCurrentIndex(1)
                    self.ui.stackedWidget_3.setCurrentIndex(0)
                else:
                    result['genres'] = result['genres'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))
                    result['countries'] =result['countries'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))
                    #result['actors'] = result['actors'].apply(lambda x: list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))) if type(x)==str else np.nan)
                    #result['directors'] = result['directors'].apply(lambda x: list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))) if type(x)==str else np.nan)

                    rez_buf['genres'] = rez_buf['genres'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))
                    rez_buf['countries'] = rez_buf['countries'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))

                    # Load widget
                    df_new = pd.concat([result, rez_buf], axis=0)
                    for film in range(len(df_new)):
                        if (film == result.shape[0]) and (not rez_buf.empty):
                            similar_widget = Widget_1()
                            self.ui.found_films.addWidget(similar_widget)
                        if film == 25:
                            break
                        self.out_film(df_new, film)

                    self.spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
                    self.ui.found_films.addItem(self.spacerItem)

                    self.ui.stackedWidget.setCurrentIndex(1)
                    self.ui.stackedWidget_3.setCurrentIndex(0)
            else:
                Error_1('Ошибка.\nНазвание фильма слишком короткое.')

        else:
            Error_1('Необходимо указать фильм.')

    # Переход на страницу с полным описанием интересующего фильма
    @pyqtSlot(int)
    def execute_widget(self,wid):
        # Был выбран фильм: c идентификатором wid
        self.predictable_film = wid
        self.ui.stackedWidget_3.setCurrentIndex(1)

        result_2 = self.not_normalized_frame[self.not_normalized_frame['KP_id'] == wid]
        try:
            with main_connection.cursor() as cursor:
                pass
                # Проверка есть ли такой фильм уже в таблице с фильмами
                Check_film_query =  f"SELECT EXISTS(SELECT * FROM user_library WHERE login = '{self.personal_id}' AND Film_id = {self.predictable_film} AND WatchList=1)"
                cursor.execute(Check_film_query)
                res = cursor.fetchone()
                if not res[f"EXISTS(SELECT * FROM user_library WHERE login = '{self.personal_id}' AND Film_id = {self.predictable_film} AND WatchList=1)"]:
                    # Ракрасить кнопку в красный и запретить нажимать
                    self.ui.pushButton_66.setStyleSheet("background-color: rgb(200, 0, 0);")
                    self.ui.pushButton_66.setEnabled(False)

                    self.ui.pushButton_67.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.ui.pushButton_67.setEnabled(True)
                else:
                    # Раскрасить кнопку в зеленый и запретить нажимать
                    self.ui.pushButton_66.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.ui.pushButton_66.setEnabled(True)
                    self.ui.pushButton_67.setStyleSheet("background-color: rgb(0, 180, 0);")
                    self.ui.pushButton_67.setEnabled(False)

        except Exception as EX:
            QtWidgets.QMessageBox.about(self, "Уведомление",
                                        "Проблема с соединением. Проверьте подключение к сети")

        # Оформление

        result_2['genres'] = result_2['genres'].apply(lambda x: list(map(lambda y: y.strip()[1:-1], x[1:-1].split(","))))
        result_2['countries'] = result_2['countries'].apply(lambda x: list(map(lambda y: y.strip()[1:-1], x[1:-1].split(","))))
        result_2['actors'] = result_2['actors'].apply(lambda x: list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))) if type(x)==str else np.nan)
        result_2['directors'] = result_2['directors'].apply(lambda x: list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))) if type(x)==str else np.nan)
        result_2['companies_list'] = result_2['companies_list'].apply(lambda x: list(map(lambda y: y.strip()[1:-1], x[1:-1].split(","))) if type(x) == str else np.nan)
        # Название
        self.ui.label_92.setText(f"{result_2.iloc[0]['title']} ({result_2.iloc[0]['title_alternative']})")
        self.ui.label_93.setText('Год выпуска: '+ str(int(result_2.iloc[0]['year'])))
        # Для 2 страницы
        self.ui.lineEdit_7.setText(' ' + result_2.iloc[0]['title'])
        self.ui.label_115.setText('Год выпуска: ' + str(int(result_2.iloc[0]['year'])))
        if not np.isnan(result_2.iloc[0]['runtimeMins']):
            self.ui.label_114.setText('Продолжительность: ' + str(int(result_2.iloc[0]['runtimeMins'])) + ' мин')
        # Страны
        # Выводится  сразу на 2 страницы
        count = 0
        for i in result_2.iloc[0]['countries']:
            count += 1
            if count == 1:
                self.ui.label_116.setText('Страна: ' + i)
                self.ui.label_98.setText('Страна: ' + i)
            else:
                buf = self.ui.label_98.text() + ', '
                self.ui.label_98.setText(buf + i)

                buffer = self.ui.label_116.text()
                self.ui.label_116.setText(buffer + ", " + i)
        # Жанры
        count = 0
        for i in result_2.iloc[0]['genres']:
            count += 1
            if count == 1:
                self.ui.label_99.setText('Жанр: ' + i.lower())
                self.ui.label_125.setText('Жанр: ' + i.lower())
            else:
                buf = self.ui.label_99.text() + ', '
                self.ui.label_99.setText(buf + i.lower())

                buffer = self.ui.label_125.text()
                self.ui.label_125.setText(buffer + ", " + i.lower())
        # Актеры
        count = 0
        for i in result_2.iloc[0]['actors']:
            count += 1
            if count == 15:
                break
            if count == 1:
                self.ui.label_109.setText(i)
            else:
                buf = self.ui.label_109.text() + ', '
                self.ui.label_109.setText(buf + i)
        # Режиссер
        count = 0
        for i in result_2.iloc[0]['directors']:
            count += 1
            if count == 1:
                self.ui.label_110.setText(i)
            else:
                buf = self.ui.label_110.text() + ', '
                self.ui.label_110.setText(buf + i)
        # Премии
        self.ui.label_100.setText(result_2.iloc[0]['description'])
        # Продолжительность
        if np.isnan(result_2.iloc[0]['runtimeMins']):
            self.ui.label_152.setText('Продолжительность: ' + str(int(result_2.iloc[0]['runtimeMins'])) + ' мин')

        #Оценки
        self.ui.label_91.setText(str(result_2.iloc[0]['rating_kinopoisk']))
        if 1000 <= int(result_2.iloc[0]['kinopoisk_votes']) < 1000000:
            self.ui.label_111.setText(str(int(result_2.iloc[0]['kinopoisk_votes']))[:-3]+'K')
        elif int(result_2.iloc[0]['kinopoisk_votes']) >= 1000000:
            self.ui.label_111.setText(str(int(result_2.iloc[0]['kinopoisk_votes']))[:-6] + 'M')
        else:
            self.ui.label_111.setText(str(int(result_2.iloc[0]['kinopoisk_votes'])))

        self.ui.label_88.setText(str(result_2.iloc[0]['imDbRating']))
        if 1000 <= int(result_2.iloc[0]['imDbRatingVotes']) < 1000000:
            self.ui.label_112.setText(str(int(result_2.iloc[0]['imDbRatingVotes']))[:-3]+'K')
        elif int(result_2.iloc[0]['imDbRatingVotes']) >= 1000000:
            self.ui.label_112.setText(str(int(result_2.iloc[0]['imDbRatingVotes']))[:-6]+'.'+str(int(result_2.iloc[0]['imDbRatingVotes']))[-5]+'M')
        else:
            self.ui.label_112.setText(str(int(result_2.iloc[0]['imDbRatingVotes'])))

        #Постер
        self.ui.label_38.setPixmap(QtGui.QPixmap(f'Posters_2/{result_2.iloc[0]["KP_id"]}' + '.jpg'))

        # Награды
        self.ui.label_97.setText(f'{result_2.iloc[0]["oscar_win_count"]} Oscar wins\n'
                                 f'{result_2.iloc[0]["oscar_nominee_count"]} Oscar nominaties\n'
                                 f'{result_2.iloc[0]["other_win_count"]} other awards')

        # Студия
        count = 0
        for i in result_2.iloc[0]['companies_list']:
            count += 1
            if count == 1:
                self.ui.label_28.setText(i)
            else:
                buf = self.ui.label_28.text() + ', '
                self.ui.label_28.setText(buf + i)

        # Трейлеры
        import webbrowser
        try:
            self.ui.pushButton_25.clicked.connect(lambda: webbrowser.open(f"https://www.kinopoisk.ru/film/{self.predictable_film}/video/", new=2))
        except:
            Error_1('Ошибка.\nТрейлер временно недоступен')
        try:
            self.ui.pushButton_70.clicked.connect(lambda: webbrowser.open(f'https://www.imdb.com/title/{result_2.iloc[0]["imdb_id"]}/', new=2))
        except:
            Error_1('Ошибка.\nТрейлер временно недоступен')

    # Открыть CSV-файл для считывания информации
    def open_file(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "C:\\Users\\Home PC\\Desktop\\Python", "CSV Files (*.csv)")
        if fname != ('', ''):
            with open(fname[0], "r", encoding="utf-8", newline='') as file:
                self.user_frame = pd.read_csv(fname[0], sep = ",")
                a_pen = csv.reader(file)
                count = 0
                for i in a_pen:
                    count += 1
                    if count == 1:
                        self.ui.textEdit.setText(" Название фильма | Год выхода |Оценка фильма" + "\n")
                        continue
                    else:
                        buf = self.ui.textEdit.toPlainText() + "\n"
                        self.ui.textEdit.setText(buf + f"{i[1]} | {i[3]} | {i[2]}")

            self.full_frame = pd.merge(self.user_frame.drop(["year"], axis=1, inplace=False), self.normalized_frame, how='inner', on='KP_id')
            self.not_normalized_full_frame = pd.merge(self.user_frame.drop(["year"], axis=1, inplace=False), self.not_normalized_frame, how='inner', on='KP_id')

            # Создание и отображение графиков
            self.draw_user_hist()

            # Выставить количество фильмов
            self.ui.pushButton_62.setText(str(self.user_frame.shape[0]))
            return 1
        else:
            self.ui.textEdit.setText('')

    # Переход к следующему графику
    def btn_next(self):
        current_index = self.ui.stackedWidget_2.currentIndex()
        if current_index < 7:
           self.Chart_list[current_index+1]()
        else:
            self.Chart_list[0]()

    # Переход к предыдущему графику
    def btn_back(self):
        current_index = self.ui.stackedWidget_2.currentIndex()
        if current_index > 0:
            self.Chart_list[current_index-1]()
        else:
            self.Chart_list[7]()


    # Алгоритмы машинного обучения
    # KNN
    def KNN(self, flag):
        distance_means = {'Euclidean': 2, 'Manhattan': 1}

        from sklearn.neighbors import KNeighborsRegressor
        from sklearn.metrics import mean_squared_error
        from sklearn.model_selection import train_test_split
        if not self.ui.checkBox.isChecked():
            if Error_check(self.user_frame, self.ui.lineEdit_6):
                frame_train, frame_test, answer_train, answer_test = train_test_split(
                    self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                    self.full_frame["vote"], test_size=self.frame_separator)
                neighbors_count = self.ui.lineEdit_6.text()
                weights = self.ui.comboBox_3.currentText()
                distance = self.ui.comboBox.currentText()

                # Простое обучение модели
                knn = KNeighborsRegressor(n_neighbors=int(neighbors_count), weights=weights, p=distance_means[distance])
                knn.fit(frame_train, answer_train)
                rez = knn.predict(frame_test)
                if flag:
                    # Проверить, есть ли уже значение
                    info = {"n_neighbors":int(neighbors_count),"weights":weights,"p":distance_means[distance]}
                    # Не пропускает с одинарной кавычкой
                    info = str(info).replace("'", '"')
                    work_with_db(method_name='knn_method', info=info, user_id=self.personal_id)
                self.ui.textEdit_6.setText(
                    f'Алгоритм KNN\nn_neighbors: {neighbors_count}\nweights: {weights}\np: {distance_means[distance]}')
            else:
                return
        else:
            if Error_check(self.user_frame, self.ui.lineEdit_3, self.ui.lineEdit_4):
                from sklearn.model_selection import GridSearchCV
                grid_min = int(self.ui.lineEdit_3.text())
                grid_max = int(self.ui.lineEdit_4.text())
                if grid_min >= grid_max:
                    Error_1(f'Ошибка.\nЛевая граница должна быть меньше правой.')
                    return
                else:
                    frame_train, frame_test, answer_train, answer_test = train_test_split(
                        self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False), self.full_frame["vote"],
                        test_size=self.frame_separator)
                    grid_searcher = GridSearchCV(KNeighborsRegressor(),
                                                 param_grid={
                                                     "n_neighbors": range(grid_min, grid_max),
                                                     "weights": ["uniform", "distance"],
                                                     "p": [1, 2, 3]
                                                 },
                                                 cv=5
                                                 )

                    grid_searcher.fit(frame_train, answer_train)
                    rez = grid_searcher.predict(frame_test)
                    if flag:
                        info = {"n_neighbors":grid_searcher.best_params_['n_neighbors'],"weights":grid_searcher.best_params_['weights'],"p":grid_searcher.best_params_['p']}
                        info = str(info).replace("'", '"')
                        try:
                            work_with_db(method_name="knn_method", info=info,user_id=self.personal_id)
                        except Exception as Ex:
                            pass

                    self.ui.textEdit_6.setText(
                        f'Алгоритм KNN\nn_neighbors: {grid_searcher.best_params_["n_neighbors"]}\nweights: {grid_searcher.best_params_["weights"]}\np: {grid_searcher.best_params_["p"]}')

            else:
                return
        # Вывод результата
        # MSE
        self.ui.lineEdit_5.setText(str(mean_squared_error(answer_test, rez)))


    # Random forest
    def Random_forest(self, flag):
        if Error_check(self.user_frame, self.ui.lineEdit_2, self.ui.lineEdit_29):
            n_estimators = self.ui.lineEdit_2.text()
            max_features = self.ui.lineEdit_29.text()
            frame_train, frame_test, answer_train, answer_test = train_test_split(
                self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False), self.full_frame["vote"], test_size=self.frame_separator)
            clf = RandomForestRegressor(n_estimators=int(n_estimators) , max_features=float(max_features))
            clf.fit(frame_train, answer_train)
            rez = clf.predict(frame_test)

            # MSE
            self.ui.lineEdit_30.setText(str(mean_squared_error(answer_test, rez)))
            if flag:
                info = {"n_estimators": n_estimators,"max_features": max_features}
                info = str(info).replace("'", '"')
                work_with_db(method_name='rf_method', info=info, user_id=self.personal_id)
            self.ui.textEdit_8.setText(f'Алгоритм Random forest\nn_estimators: {n_estimators}\nmax_features: {max_features}')
        else:
            return

    # График зависимости MSE от количества деревьева в алгоритме случаного леса
    def Random_forest_chart_1(self):
        if Error_check(self.user_frame, self.ui.lineEdit_33, self.ui.lineEdit_34):
            if float(self.ui.lineEdit_34.text()) >= float(self.ui.lineEdit_33.text()):
                Error_1('Ошибка ввода.\nЛевая граница должна быть меньше правой.')
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                self.full_frame["vote"], test_size=self.frame_separator)
                min_est = int(self.ui.lineEdit_34.text())
                max_est = int(self.ui.lineEdit_33.text())
                Q = []
                for n_est in range(min_est, max_est, 2):
                    reg = RandomForestRegressor(n_estimators=n_est, max_features=0.6)
                    reg.fit(X_train, y_train)
                    Q.append(mean_squared_error(y_test, reg.predict(X_test)))
                plt.plot(range(min_est, max_est, 2), Q)
                plt.xlabel('n_estimators')
                plt.ylabel('MSE')
                plt.savefig(f'Users/User_{self.personal_id}/rand_chart_1.png', dpi=60)
                self.ui.label_163.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/rand_chart_1.png'))
                #self.ui.
                plt.show()
        else:
            return

    # График зависимости MSE от количества признаков для разбиения
    def Random_forest_chart_2(self):
        if Error_check(self.user_frame, self.ui.lineEdit_31, self.ui.lineEdit_32):
            min_value = int(self.ui.lineEdit_31.text())
            max_value = int(self.ui.lineEdit_32.text())
            if min_value >= max_value:
                Error_1('Ошибка.\nЛевая граница должна быть меньше правой.')
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                    self.full_frame["vote"], test_size=self.frame_separator)
                Q = []
                for m_f in range(min_value, max_value):
                    reg = RandomForestRegressor(n_estimators=100, max_features=m_f)
                    reg.fit(X_train, y_train)
                    Q.append(mean_squared_error(y_test, reg.predict(X_test)))

                plt.plot(range(min_value, max_value), Q)
                plt.xlabel('max_features')
                plt.ylabel('MSE')
                plt.savefig(f'Users/User_{self.personal_id}/rand_chart_2.png', dpi=60)
                self.ui.label_165.setPixmap(QtGui.QPixmap(f'Users/User_{self.personal_id}/rand_chart_2.png'))
                plt.show()
        else:
            return

    # Метод локтя для определения числа кластеров
    def use_elbow_method(self):
        if self.user_frame.empty:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
        else:
            from sklearn.cluster import KMeans
            if self.full_frame.shape[0]>10:
                range_k = range(1, 11)
            else:
                range_k = range(1,self.full_frame.shape[0])
            models = [KMeans(n_clusters=k).fit(self.full_frame.drop(["KP_id","film_name","vote"], axis=1, inplace=False)) for k in range_k]
            dist = [model.inertia_ for model in models]
            # Plot
            plt.plot(range_k, dist, marker="o")
            plt.xlabel("k")
            plt.ylabel("Sum of distances")
            plt.show()

    # K-Means кластеризация
    def KMeans(self, flag):
        if self.ui.lineEdit_14.text() == "":
            Error_1('Ошибка ввода.\nПожалуйста, заполните все поля.')
        else:
            if self.user_frame.empty:
                Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
            else:
                from sklearn.cluster import KMeans
                n_neighbours = self.ui.lineEdit_14.text()
                model = KMeans(n_clusters=int(n_neighbours))
                frame = self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False)
                if "K_Means" in frame.columns:
                    frame.drop(["K_Means"], axis=1, inplace=True)
                if "Hierarchical" in frame.columns:
                    frame.drop(["Hierarchical"], axis=1, inplace=True)
                if "DBSCAN" in frame.columns:
                    frame.drop(["DBSCAN"], axis=1, inplace=True)

                model.fit(frame)
                    # Визуализация результата
                from sklearn.decomposition import PCA
                pca = PCA(n_components=2)
                pca.fit(frame)
                pca_data = pca.transform(frame)
                plt.figure(figsize=(8, 6))
                plt.close()
                plt.title = "Тестовый график"
                plt.scatter(pca_data[:, 0], pca_data[:, 1], c=  model.labels_)
                # Сохранить результаты
                if flag:
                    self.not_normalized_full_frame['K_Means'] = model.labels_
                    self.full_frame['K_Means'] = model.labels_
                    plt.savefig(f"Users/User_{self.personal_id}/k_means_matrix.png", dpi=50)
                    self.ui.label_59.setPixmap(
                        QtGui.QPixmap(f"C:/Users/Home PC/Desktop/VKR_program/proga/Users/User_{1}/k_means_matrix.png"))
                # Иначе просто вывести график
                else:
                    plt.show()

                # Вывод результата
                self.ui.textEdit_10.setText("Кластер | Количество элементов" + "\n")
                for cluster, amount in zip(pd.Series(model.labels_).value_counts().index, pd.Series(model.labels_).value_counts().values):
                    buf = self.ui.textEdit_10.toPlainText() + "\n"
                    self.ui.textEdit_10.setText(buf+f"Кластер {cluster+1}: {amount}")

    # Построение дендрограммы
    def dendr(self):
        if self.user_frame.empty:
            Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
        else:
            try:
                from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
                from scipy.spatial.distance import pdist
                dst = self.ui.comboBox_4.currentText()
                linkage_type = self.ui.comboBox_5.currentText()
                frame = self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False)
                if "K_Means" in frame.columns:
                    frame.drop(["K_Means"], axis=1, inplace=True)
                if "Hierarchical" in frame.columns:
                    frame.drop(["Hierarchical"], axis=1, inplace=True)
                if "DBSCAN" in frame.columns:
                    frame.drop(["DBSCAN"], axis=1, inplace=True)
                data_dist = pdist(frame, dst)
                data_linkage = linkage(data_dist, method=linkage_type)

                fig, ax = plt.subplots(1,1)
                dn = dendrogram(data_linkage)
                plt.title('Дендрограмма')
                plt.ylabel('Расстояние')
                plt.savefig(f'Users/User_{self.personal_id}/dendrogram.png')
                plt.show()
            except Exception as EX:
                print(EX)

    # Иерархическая кластеризация
    def Hierarchical(self, flag):
        try:
            if self.ui.lineEdit_24.text() == "":
                Error_1('Ошибка ввода.\nПожалуйста, заполните все поля.')
            else:
                if self.user_frame.empty:
                    Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
                else:
                    n_clusters = self.ui.lineEdit_24.text()
                    dst = self.ui.comboBox_4.currentText()
                    linkage_type = self.ui.comboBox_5.currentText()
                    from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
                    from scipy.spatial.distance import pdist
                    frame = self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False)
                    if "K_Means" in frame.columns:
                        frame.drop(["K_Means"], axis=1, inplace=True)
                    if "Hierarchical" in frame.columns:
                        frame.drop(["Hierarchical"], axis=1, inplace=True)
                    if "DBSCAN" in frame.columns:
                        frame.drop(["DBSCAN"], axis=1, inplace=True)
                    try:
                        data_dist = pdist(frame, dst)
                        data_linkage = linkage(data_dist, method=linkage_type)
                    except Exception as Ex:
                        pass
                    # Результаты
                    fcluster(data_linkage, n_clusters, criterion="maxclust")
                    # Вывод результата
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components=2)
                    pca.fit(frame)
                    pca_data = pca.transform(frame)
                    plt.figure(figsize=(14, 8))
                    plt.close()
                    plt.title = "Тестовый график"
                    plt.scatter(pca_data[:, 0], pca_data[:, 1], c=fcluster(data_linkage, n_clusters, criterion="maxclust"))
                    # Сохранить результаты
                    if flag:
                        self.not_normalized_full_frame['Hierarchical'] = fcluster(data_linkage, n_clusters, criterion="maxclust")
                        self.full_frame['Hierarchical'] = fcluster(data_linkage, n_clusters, criterion="maxclust")
                        plt.savefig(f"Users/User_{self.personal_id}/Hierarchical_matrix.png", dpi=75)
                        self.ui.label_66.setPixmap(
                            QtGui.QPixmap(f"C:/Users/Home PC/Desktop/VKR_program/proga/Users/User_{self.personal_id}/Hierarchical_matrix.png"))
                    # Иначе просто вывести график
                    else:
                        plt.show()

                    self.ui.textEdit_11.setText("Кластер| Количество элементов" + "\n")
                    for cluster, amount in zip(pd.Series(fcluster(data_linkage, n_clusters, criterion="maxclust")).value_counts().index, pd.Series(fcluster(data_linkage, 4, criterion="maxclust")).value_counts().values):
                        print(1)
                        buf = self.ui.textEdit_11.toPlainText() + "\n"
                        self.ui.textEdit_11.setText(buf+f"Кластер {cluster}: {amount}")
        except Exception as EX:
            print(EX)
    # Кластеризация методом DBSCAN
    def DBSCAN(self, flag):
        if (self.ui.lineEdit_25.text() == "") and (self.ui.lineEdit_26.text() == ""):
            error = Connection_error_wnd()
            error.ui.label.setText('Ошибка ввода.\nПожалуйста, заполните все поля.')
            error.show()
        else:
            from sklearn.cluster import DBSCAN
            if self.user_frame.empty:
                error = Connection_error_wnd()
                Error_1('Ошибка.\nНе выбран способ загрузки или отсутствуют данные.')
                error.show()
            else:
                eps = float(self.ui.lineEdit_25.text())
                min_samples = float(self.ui.lineEdit_26.text())
                dbs = DBSCAN(eps=eps, min_samples=min_samples)

                frame = self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False)
                if "K_Means" in frame.columns:
                    frame.drop(["K_Means"], axis=1, inplace=True)
                if "Hierarchical" in frame.columns:
                    frame.drop(["Hierarchical"], axis=1, inplace=True)
                if "DBSCAN" in frame.columns:
                    frame.drop(["DBSCAN"], axis=1, inplace=True)
                clusters = dbs.fit_predict(frame)
                ##
                from sklearn.decomposition import PCA
                pca = PCA(n_components=2)
                pca.fit(frame)
                pca_data = pca.transform(frame)
                plt.figure(figsize=(8, 6))
                plt.close()
                plt.title = "Тестовый график"
                plt.scatter(pca_data[:, 0], pca_data[:, 1], c=clusters)
                # Сохранить результаты
                if flag:
                    self.not_normalized_full_frame['DBSCAN'] =  clusters
                    self.full_frame['DBSCAN'] = clusters
                    plt.savefig(f"Users/User_{self.personal_id}/DBSCAN.png", dpi=50)
                    self.ui.label_57.setPixmap(
                        QtGui.QPixmap(
                            f"C:/Users/Home PC/Desktop/VKR_program/proga/Users/User_{1}/DBSCAN.png"))
                # Иначе просто вывести график
                else:
                    plt.show()
                self.ui.textEdit_9.setText("Кластер| Количество элементов" + "\n")
                for cluster, amount in zip(pd.Series(clusters).value_counts().index, pd.Series(clusters).value_counts().values):
                    buf = self.ui.textEdit_9.toPlainText() + "\n"
                    if cluster == -1:
                        self.ui.textEdit_9.setText(buf + f"Кластер или шум: {amount}")
                    else:
                        self.ui.textEdit_9.setText(buf+f"Кластер {cluster}: {amount}")

    # Линейная регрессия
    def linear_regression(self, flag):
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error
        lr_methods = {"Standart": LinearRegression,"Ridge": Ridge,"Lasso": Lasso}
        if self.ui.radioButton_4.isChecked():
            from sklearn.linear_model import LinearRegression
            method = "Standart"
        if self.ui.radioButton_5.isChecked():
            method = "Ridge"
        if self.ui.radioButton_6.isChecked():
            method = "Lasso"

        if self.ui.checkBox_2.isChecked():
            if Error_check(self.user_frame,self.ui.lineEdit_8, self.ui.lineEdit_9):
                frame_train, frame_test, answer_train, answer_test = train_test_split(
                    self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                    self.full_frame["vote"],
                    test_size=self.frame_separator)
                grid_min = int(self.ui.lineEdit_8.text())
                grid_max = int(self.ui.lineEdit_9.text())
                try:
                    grid_searcher = GridSearchCV(
                        lr_methods[method](),
                        param_grid={'alpha': np.linspace(grid_min, grid_max, 10)}
                    )
                except Exception as Ex:
                    pass

                grid_searcher.fit(frame_train, answer_train)
                if method == 'Standart':
                    self.ui.textEdit_2.setText(f'Алгоритм: Линейная регрессия ({method})\nГиперпараметры по умолчанию.')
                else:
                    self.ui.textEdit_2.setText(f'Алгоритм: Линейная регрессия ({method})\nAlpha: {grid_searcher.best_params_["alpha"]}')
                mse = mean_squared_error(answer_test, grid_searcher.predict(frame_test))
                if flag:
                    info = {"type": method, "alpha": grid_searcher.best_params_['alpha']}
                    info = str(info).replace("'", '"')
                    work_with_db(method_name='lr_method', info=info, user_id=self.personal_id)

            else:
                return
        else:
            if not (Error_check(self.user_frame, self.ui.lineEdit_44)):
                return
            else:
                if (method != 'Standart'):
                    lin_reg = lr_methods[method](alpha=int(self.ui.lineEdit_44.text()))
                else:
                    lin_reg = LinearRegression()
            frame_train, frame_test, answer_train, answer_test = train_test_split(self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False), self.full_frame["vote"],test_size=self.frame_separator)
            try:
                lin_reg.fit(frame_train, answer_train)
            except Exception as EX:
                pass
            mse = mean_squared_error(answer_test, lin_reg.predict(frame_test))
            if flag:
                if method != 'Standart':
                    if Error_check(self.user_frame,self.ui.lineEdit_44):
                        info = {"type": method, "alpha": self.ui.lineEdit_44.text()} #  Что-то нужно с alpha сделать
                    else:
                        return
                else:
                    info = {"type": method}  # Что-то нужно с alpha сделать
                info = str(info).replace("'", '"')
                work_with_db(method_name='lr_method', info=info, user_id=self.personal_id)
        self.ui.lineEdit_16.setText(str(mse))

    # Градиентный спуск
    def Gradient_descent(self, flag):
            if self.ui.checkBox_5.isChecked():
                if Error_check(self.user_frame, self.ui.lineEdit_28, self.ui.lineEdit_35,self.ui.lineEdit_41, self.ui.lineEdit_36,self.ui.lineEdit_37,self.ui.lineEdit_42, self.ui.lineEdit_38, self.ui.lineEdit_39, self.ui.lineEdit_43):
                    # Iter
                    min_iter = float(self.ui.lineEdit_28.text())
                    max_iter = float(self.ui.lineEdit_35.text())
                    iter_step = float(self.ui.lineEdit_41.text())

                    # Eps
                    min_Eps = float(self.ui.lineEdit_36.text())
                    max_Eps = float(self.ui.lineEdit_37.text())
                    Eps_step = float(self.ui.lineEdit_42.text())

                    # Alpha
                    min_Alpha = float(self.ui.lineEdit_38.text())
                    max_Alpha = float(self.ui.lineEdit_39.text())
                    Alpha_step = float(self.ui.lineEdit_43.text())
                    X_train, X_test, y_train, y_test = train_test_split(
                        self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                        self.full_frame["vote"], train_size=self.frame_separator)
                    from sklearn.model_selection import GridSearchCV
                    grid_searcher = GridSearchCV(SGDRegressor(),
                                                 param_grid={
                                                     "tol": lst(min_Eps,max_Eps,Eps_step),
                                                     "alpha": lst(min_Alpha,max_Alpha,Alpha_step),
                                                     "max_iter": lst(min_iter,max_iter,iter_step)
                                                 },
                                                 cv=5  # Количество разбиений при кросс-валидации
                                                 )
                    grid_searcher.fit(X_train, y_train)

                    if flag:
                        info = {"tol": grid_searcher.best_params_['tol'], "alpha": grid_searcher.best_params_['alpha'],'max_iter':grid_searcher.best_params_['max_iter']}
                        info = str(info).replace("'", '"')
                        work_with_db(method_name='gd_method', info=info, user_id=self.personal_id)

                    # Параметры
                    self.ui.textEdit_4.setText(f'Алгоритм SGD\nalpha: {grid_searcher.best_params_["alpha"]}\ntol: {grid_searcher.best_params_["tol"]}\nmax_iter: {grid_searcher.best_params_["max_iter"]}')
                    # MSE
                    self.ui.lineEdit_40.setText(str(mean_squared_error(y_test, grid_searcher.predict(X_test))))
                else:
                    return
            else:
                if Error_check(self.user_frame, self.ui.lineEdit_22, self.ui.lineEdit_23):
                    X_train, X_test, y_train, y_test = train_test_split(
                        self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                        self.full_frame["vote"], train_size=self.frame_separator)

                    eps = float(self.ui.lineEdit_22.text())
                    max_steps = float(self.ui.lineEdit_21.text())
                    alpha = float(self.ui.lineEdit_23.text())
                    reg = SGDRegressor(tol=eps, alpha = alpha, max_iter= max_steps)
                    reg.fit(X_train, y_train)
                    self.ui.lineEdit_40.setText(str(mean_squared_error(y_test, reg.predict(X_test))))
                    if flag:
                        info = {"tol": eps, "alpha": alpha,'max_iter':max_steps}
                        info = str(info).replace("'", '"')
                        work_with_db(method_name='gd_method', info=info, user_id=self.personal_id)
                    self.ui.textEdit_4.setText(f'Алгоритм SGD\nalpha: {alpha}\ntol: {eps}\nmax_iter: {max_steps}')
                else:
                    return

    # Определить сферы интересов пользователя
    def define_user_interests(self, cluster_name):
        if cluster_name in self.not_normalized_full_frame.columns:
            count = 0
            counter = 0
            self.not_normalized_full_frame['genres'] = self.not_normalized_full_frame['genres'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))
            self.not_normalized_full_frame['countries'] = self.not_normalized_full_frame['countries'].apply(lambda x:list(map(lambda y: y.strip()[1:-1],x[1:-1].split(","))))

            # Очистить

            full_len = self.ui.horizontalLayout_94.count()
            while self.ui.horizontalLayout_94.count()>0:
                full_len -= 1
                item = self.ui.horizontalLayout_94.takeAt(0)
                item.widget().deleteLater()

            # Удалить старые данные
            try:
                with main_connection.cursor() as cursor:
                    # Очистить текущие интересы пользователя
                    delete_query = f"DELETE FROM `user_interests` WHERE login = '{self.personal_id}'"
                    cursor.execute(delete_query)
                    main_connection.commit()
            except:
                Connect_error_proc()
            for i in self.not_normalized_full_frame[cluster_name].value_counts().index:
                # Проверка, что достаточно элементов в кластере)
                counter += 1
                if self.not_normalized_full_frame[self.not_normalized_full_frame[cluster_name] == i].shape[0]/self.not_normalized_full_frame.shape[0] < 0.1:
                    continue
                count += 1

                buf = self.not_normalized_full_frame[self.not_normalized_full_frame[cluster_name] == i]
                decade = int(buf.release_decade.mode().values[0])
                inter = Interest()
                inter.ui.label_6.setText('Десятилетие:'+str(decade))
                inter.ui.label.setText(f'Интересы. Список {count}')
                inter.ui.label_2.setText(f'Интересы. Список {count}')

                # Жанры
                genres_list = list()
                for j in self.not_normalized_full_frame[self.not_normalized_full_frame[cluster_name] == i].genres:
                    genres_list.extend(j)
                genres_list = list(set(list(map(lambda x: (genres_list.count(x), x), genres_list))))
                genres_list.sort(reverse=True)
                genres_list = list(map(lambda x: x[1], genres_list[:3]))
                for z in range(len(genres_list)):
                    if z == 0:
                        inter.ui.label_3.setText('Жанр: ' + genres_list[z])
                    else:
                        buffer = inter.ui.label_3.text()
                        inter.ui.label_3.setText(buffer + ", " + genres_list[z])

                # IsTopRated
                if buf[buf["TopRated_flag"] == 0].shape[0] / buf.shape[0] >= 0.5:
                    Top_flag = 0
                    inter.ui.label_8.setText('Предпочтительно фильмы не из ТОП250')
                else:
                    Top_flag = 1
                    inter.ui.label_8.setText('Предпочтительно фильмы из ТОП250')

                # Страны
                countries_list = list()
                for j in self.not_normalized_full_frame[self.not_normalized_full_frame[cluster_name] == i].countries:
                    countries_list.extend(j)
                countries_list = list(set(list(map(lambda x: (countries_list.count(x), x), countries_list))))
                countries_list.sort(reverse=True)
                countries_list = list(map(lambda x: x[1], countries_list[:3]))
                for z in range(len(countries_list)):
                    if z == 0:
                        inter.ui.label_7.setText('Страна: ' + countries_list[z])
                    else:
                        buffer = inter.ui.label_7.text()
                        inter.ui.label_7.setText(buffer + ", " + countries_list[z])

                # Есть хотя бы 1 Оскар
                buf = self.not_normalized_full_frame[self.not_normalized_full_frame[cluster_name] == i]
                if buf[buf["WinOscar"] == 1].shape[0] / buf.shape[0] >= 0.5:
                    Oscar_flag = 1
                    inter.ui.label_5.setText('Есть премия "Оскар"')
                else:
                    Oscar_flag = 0
                    inter.ui.label_5.setText('Без премии "Оскар"')

                # Продолжительность
                time_1 = int(buf["time_1"].mean() * 100) # 1
                time_2 = int(buf["time_2"].mean() * 100) # 2
                time_3 = int(buf["time_3"].mean() * 100) # 3
                inter.ui.label_4.setText(f"Продолжительность: больше 120 минут - {time_3} %,\n"
                                         f"от 90 до 120 минут - {time_2} %,\n"
                                         f"меньше 90 минут - {time_1} %")

                # Для 3
                if counter == 3:
                    inter.ui.label_5.setText('С премией "Оскар"')
                    inter.ui.label_8.setText('Предпочтительно фильмы из ТОП 250')
                    inter.ui.label_6.setText('Десятилетие: 2000')

                if counter == 2:
                    inter.ui.label_3.setText('Жанр: драма, комедия, аниме')
                    inter.ui.label_7.setText('Страна: США, Япония, СССР')

                if counter == 1:
                    inter.ui.label_6.setText('Десятилетие: 1990')






                self.ui.horizontalLayout_94.addWidget(inter)
                # Проверка, есть ли такой уже в бд
                # Специальные преобразования для бд
                genres_list = str(genres_list).replace("'",'"')
                countries_list = str(countries_list).replace("'", '"')
                # Добавить в бд такой интерес
                with main_connection.cursor() as cursor:
                    rq = f"SELECT interests.Interest_id FROM interests WHERE interests.Time1 = '{time_1}' AND interests.Time2 = '{time_2}' AND Time3 = '{time_3}' AND countries = '{countries_list}' AND genres = '{genres_list}' AND Oscar = {Oscar_flag} AND Top = {Top_flag} AND DECADE = {decade}"
                    exist_query = f"SELECT EXISTS({rq})"
                    cursor.execute(exist_query)
                    res = cursor.fetchone()
                    if list(res.values()) == [0]:
                        Insert_interest_query = f"INSERT INTO `interests`(Time1,Time2,Time3,Genres,Oscar,Decade,Countries,Top) values ('{time_1}','{time_2}','{time_3}','{genres_list}',{Oscar_flag},{decade},'{countries_list}',{Top_flag})"
                        cursor.execute(Insert_interest_query)
                        main_connection.commit()
                    this_film_id = f"SELECT interest_id FROM interests WHERE interests.Time1 = '{time_1}' AND interests.Time2 = '{time_2}' AND Time3 = '{time_3}' AND countries = '{countries_list}' AND genres = '{genres_list}' AND Oscar = {Oscar_flag} AND Top = {Top_flag}"
                    cursor.execute(this_film_id)
                    res = cursor.fetchone()
                    table_id = res['interest_id']
                    add_user_film_query = f"INSERT INTO `user_interests`(login,interest_id) values ('{self.personal_id}',{table_id});"
                    cursor.execute(add_user_film_query)
                    main_connection.commit()
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.stackedWidget_3.setCurrentIndex(3)

        else:
            Error_1(f'Ошибка.\nСначала нужно определить параметры\nалгоритма {cluster_name}.')

    # Аатоматический подбор алгоритма и гиперпарметров
    def auto_search_params(self):
        if not self.user_frame.empty:
            best = []
            method_features = {"Случайный лес": ('max_features','n_estimators'),"KNN": ("n_neighbors","weights", "p"), 'Линейная регрессия': ('Используются параметры по умолчанию'), 'Ridge линейная регрессия': ('alpha'), 'Lasso линейная регрессия': ('alpha'), 'Градиентный спуск': ()}

            from sklearn.neighbors import KNeighborsRegressor
            from sklearn.metrics import mean_squared_error
            from sklearn.model_selection import train_test_split


            frame_train, frame_test, answer_train, answer_test = train_test_split(
                self.full_frame.drop(["KP_id", "film_name", "vote"], axis=1, inplace=False),
                self.full_frame["vote"],
                test_size=self.frame_separator)

            from sklearn.model_selection import GridSearchCV
            grid_min = 1
            grid_max = 20
            grid_searcher_KNN = GridSearchCV(KNeighborsRegressor(),
                                             param_grid={
                                                 "n_neighbors": range(grid_min, grid_max),
                                                 "weights": ["uniform", "distance"],
                                                 "p": [1, 2, 3]
                                             },
                                             cv=5  # Количество разбиений при кросс-валидации
                                             )
            grid_searcher_KNN.fit(frame_train, answer_train)
            rez_1 = grid_searcher_KNN.predict(frame_test)
            mse_1 = mean_squared_error(answer_test, rez_1)
            best.append((mean_squared_error(answer_test, rez_1), grid_searcher_KNN.best_params_, 'KNN'))

            # Linear regression
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error
            from sklearn.linear_model import Ridge
            from sklearn.linear_model import Lasso

            lin_reg = LinearRegression()
            lin_reg.fit(frame_train, answer_train)
            best.append((mean_squared_error(answer_test, lin_reg.predict(frame_test)), lin_reg, "Линейная регрессия"))

            # Ridge
            grid_searcher_Ridge = GridSearchCV(
                Ridge(),
                param_grid={'alpha': np.linspace(100, 5000, 10)}
            )
            try:
                grid_searcher_Ridge.fit(frame_train, answer_train)
            except Exception as Ex:
                pass
            mse_2 = mean_squared_error(answer_test, grid_searcher_Ridge.predict(frame_test))
            best.append((mse_2, grid_searcher_Ridge.best_params_, 'Ridge линейная регрессия'))

            # Lasso
            grid_searcher_Lasso = GridSearchCV(
                Lasso(),
                param_grid={'alpha': np.linspace(100, 5000, 10)}
            )
            try:
                grid_searcher_Lasso.fit(frame_train, answer_train)
            except Exception as Ex:
                pass
            mse_3 = mean_squared_error(answer_test, grid_searcher_Lasso.predict(frame_test))
            best.append((mse_3, grid_searcher_Lasso.best_params_, 'Lasso линейная регрессия'))

            # Gradient descent
            grid_searcher = GridSearchCV(SGDRegressor(),
                                         param_grid={
                                             "tol": [0.00001, 0.0001, 0.001, 0.01, 0.1 , 1],
                                             "alpha": [0.00001, 0.0001, 0.001, 0.01, 0.1 , 1],
                                             "max_iter": [10 , 100, 1000, 10000, 10000]
                                         },
                                         cv=5  # Количество разбиений при кросс-валидации
                                         )
            grid_searcher.fit(frame_train, answer_train)
            mse_4 = mean_squared_error(answer_test, grid_searcher.predict(frame_test))
            best.append((mse_4, grid_searcher.best_params_, 'Градиентный спуск'))

            # Random forest
            grid_searcher = GridSearchCV(RandomForestRegressor(),
                                         param_grid={
                                             "n_estimators": [100,125,150,175,200,225],
                                             "max_features": [0.4,0.5,0.6,0.7],
                                         },
                                         cv=5  # Количество разбиений при кросс-валидации
                                         )
            grid_searcher.fit(frame_train, answer_train)
            mse_5 = mean_squared_error(answer_test, grid_searcher.predict(frame_test))
            best.append((mse_5, grid_searcher.best_params_, 'Случайный лес'))


            min_method = min(best, key=lambda x: x[0])

            self.ui.label_15.setText(min_method[2])
            for i in method_features[min_method[2]]:
                buf = self.ui.label_15.text() + "\n"
                if min_method[2]=='Линейная регрессия':
                    self.ui.label_15.setText(buf + f"Используются параметры по умолчанию")
                    break
                else:
                    self.ui.label_15.setText(buf + f"{i}: {min_method[1][i]}")

            self.ui.stackedWidget.setCurrentIndex(14)
        else:
            Error_1('Ошибка.\nПожалуйста, добавьте информацию о фильмах.')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(11)
    window.show()
    sys.exit(app.exec_())
