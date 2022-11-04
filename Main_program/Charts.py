from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice

from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui

import pandas as pd


from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QBarSet, \
    QPercentBarSeries, QBarCategoryAxis, QBarSeries,QStackedBarSeries,QHorizontalStackedBarSeries, QHorizontalBarSeries
import sys
import sys
from PyQt5.QtGui import QIcon
import statistics as stats
from PyQt5.QtWidgets import QApplication, QMainWindow

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt

# Работа с данными
import csv
import numpy as np

user_frame_not_normalized = pd.read_csv("C:/Users/Home PC/Desktop/Python/VKR/Parsing_dataset/user_full_frame.csv", sep = ",")


# User_WA = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='WinAwards').vote.mean()))
# User_TR = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='isTopRated').vote.mean()))
#
# KP_WA = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='WinAwards').rating_kinopoisk.mean()))
# KP_TR = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='isTopRated').rating_kinopoisk.mean()))
#
# IMDB_WA = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='WinAwards').imDbRating.mean()))
# IMDB_TR = list(map(lambda x: round(x,2),user_frame_not_normalized.groupby(by='isTopRated').imDbRating.mean()))



labels = ["Нет кинонаград", "Есть кинонаграды", 'Не входит в ТОП250 IMDB', 'Входит в ТОП250 IMDB']
# user = [User_WA[0],User_WA[1],User_TR[0],User_TR[1]]
# kp =[KP_WA[0],KP_WA[1],KP_TR[0],KP_TR[1]]
# imdb = [IMDB_WA[0],IMDB_WA[1],IMDB_TR[0],IMDB_TR[1]]

x = np.arange(len(labels))  # the label locations
width = 0.2# the width of the bars


# Класс графика разницы в оценках для разных значений параметров
class Window_1(QWidget):
    def __init__(self, user_data=None,film_data=None): # Передача в конструктор наборов данных: о пользователе и о признаках фильмов
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how ='inner', on ='KP_id')

        # Сформировать 4 множества с соответствующими названиями
        set0 = QBarSet("Пользователь")
        set1 = QBarSet("Кинопоиск")
        set2 = QBarSet("IMDb")
        set3 = QBarSet("Критики")

        # Формирование информации
        self.User_WA = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='WinOscar').vote.mean()))
        self.User_TR = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='TopRated_flag')['vote'].mean()))
        self.KP_WA = list(
            map(lambda x: round(x, 2), self.full_frame.groupby(by='WinOscar').rating_kinopoisk.mean()))
        self.KP_TR = list(
            map(lambda x: round(x, 2), self.full_frame.groupby(by='TopRated_flag').rating_kinopoisk.mean()))

        self.IMDB_WA = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='WinOscar').imDbRating.mean()))
        self.IMDB_TR = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='TopRated_flag').imDbRating.mean()))

        self.Critics_WA = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='WinOscar').CriticsVote.mean()))
        self.Critics_TR = list(map(lambda x: round(x, 2), self.full_frame.groupby(by='TopRated_flag').CriticsVote.mean()))

        # Добавить информацию в каждое множество
        set0.append([self.User_WA[0],self.User_WA[1],self.User_TR[0],self.User_TR[1]])
        set1.append([self.KP_WA[0],self.KP_WA[1],self.KP_TR[0],self.KP_TR[1]])
        set2.append([self.IMDB_WA[0],self.IMDB_WA[1],self.IMDB_TR[0],self.IMDB_TR[1]])
        set3.append([self.Critics_WA[0], self.Critics_WA[1], self.Critics_TR[0], self.Critics_TR[1]])

        series = QBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)
        series.append(set1)
        series.append(set2)
        series.append(set3)


        # Создать график и добавитьб серию
        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>Разница в оценках</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 9))

        # Название для каждой группы
        categories = ["Нет премии Оскар", "Есть премия Оскар", "Не входит в ТОП250 IMDb", "Входит в ТОП250 IMDb"]

        axis = QBarCategoryAxis()
        axis.append(categories)
        axis.setLabelsFont(QFont('Arial', 8))
        self.chart.createDefaultAxes()         # Создать оси
        self.chart.setAxisX(axis, series)


class Window_2(QWidget):
    def __init__(self, user_data=None,film_data=None):
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how ='inner', on ='KP_id')

        # window requirements
        self.setGeometry(200, 200, 1000, 600)
        self.setWindowTitle("Creating Barchart")
        self.setWindowIcon(QIcon("python.png"))

        # create barseries
        set0 = QBarSet('Средняя оценка пользователя')
        set1 = QBarSet("Средняя оценка на Кинопоиске")
        set2 = QBarSet("Средняя оценка на IMDb")
        set3 = QBarSet("Средняя оценка критиков")
        set4 = QBarSet("Самая частая оценка пользователя")

        # insert data to the barseries
        set0.append([round(self.full_frame.vote.mean(),3)])
        set1.append([round(self.full_frame.rating_kinopoisk.mean(),3)])
        set2.append([round(self.full_frame.imDbRating.mean(),3)])
        set3.append([round(self.full_frame.CriticsVote.mean(),3)])
        set4.append([round(self.full_frame.vote.agg(stats.mode), 3)])

        # we want to create percent bar series
        series = QBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)
        series.append(set1)
        series.append(set2)
        series.append(set3)
        series.append(set4)


        # create chart and add the series in the chart
        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>Разница в оценках</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 8))

        # create axis for the chart
        categories = ["Оценки"]

        axis = QBarCategoryAxis()
        axis.append(categories)
        axis.setLabelsFont(QFont('Arial', 10))
        self.chart.createDefaultAxes()
        self.chart.setAxisX(axis, series)


# 4 графика
class Window_4(QWidget):
    def __init__(self, user_data=None, film_data=None):
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how='inner', on='KP_id')

        # window requirements
        self.setGeometry(200, 200, 300, 100)

        set0 = QBarSet("Самая частая оценка при данном количестве премий Оскар")
        set0.append(self.full_frame.groupby(by='oscar_win_count')['vote'].agg(stats.mode))
        print('Оценки: ',self.full_frame.groupby(by='oscar_win_count')['vote'].agg(stats.mode))
        print(self.full_frame.groupby(by='oscar_win_count')['vote'].mean().values)
        print(set0)

        # we want to create percent bar series
        series = QHorizontalStackedBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)
        # create chart and add the series in the chart
        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>Распределение оценки при изменении количества премий «Оскар»</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 12))

        # create axis for the chart
        lst = map(lambda x: str(x)+' шт.',self.full_frame.groupby(by='oscar_win_count')['vote'].agg(stats.mode).index)
        categories = lst

        axis = QBarCategoryAxis()
        axis.append(categories)
        axis.setLabelsFont(QFont('Arial', 10))
        self.chart.createDefaultAxes()
        self.chart.setAxisY(axis, series)


class Window_5(QWidget):
    def __init__(self, user_data=None, film_data=None):
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how='inner', on='KP_id')

        # window requirements
        self.setGeometry(200, 200, 1000, 600)

        set0 = QBarSet("Средняя оценка")
        set0.append(self.full_frame.groupby(by='release_decade')['vote'].mean().values)

        # we want to create percent bar series
        series = QStackedBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)

        # create chart and add the series in the chart
        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>Средняя оценка для десятилетий выхода фильмов</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 10))

        # create axis for the chart
        lst = map(lambda x: str(int(x)),self.full_frame.groupby(by='release_decade')['vote'].mean().index)
        categories = lst

        axis = QBarCategoryAxis()
        #axis.setLabelsAngle(-90)
        axis.append(categories)
        self.chart.createDefaultAxes()
        self.chart.setAxisX(axis, series)
        axis.setLabelsFont(QFont('Arial', 10))


class Window_6(QWidget):
    def __init__(self, user_data=None, film_data=None):
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how='inner', on='KP_id')

        self.setGeometry(200, 200, 1000, 600)

        set0 = QBarSet("Количество оцененных фильмов по году выхода")
        set0.append(self.full_frame['year'].value_counts().values)
        series = QStackedBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)

        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>График зависимости заинтересованности в просмотре от года выхода фильма</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 10))
        # create axis for the chart
        #print(user_frame_not_normalized.groupby(by='Oscars_amount')['vote'].mean().index)
        lst = map(str,self.full_frame['year'].value_counts().index)
        categories = lst

        axis = QBarCategoryAxis()
        axis.setLabelsAngle(-90)
        axis.append(categories)
        self.chart.createDefaultAxes()
        self.chart.setAxisX(axis, series)
        axis.setLabelsFont(QFont('Arial', 10))

class Window_7(QWidget):
    def __init__(self, user_data=None,film_data=None):
        super().__init__()
        self.user_data = user_data
        self.film_data = film_data
        self.full_frame = pd.merge(self.user_data, self.film_data, how ='inner', on ='KP_id')

        self.setGeometry(200, 200, 1000, 600)

        set0 = QBarSet("Медианное значение количества оценок на Кинопоиске")
        set1 = QBarSet("Медианное значение количества оценок на IMDb")

        set0.append(self.full_frame.groupby(by='vote')['kinopoisk_votes'].agg(stats.median).values)
        set1.append(self.full_frame.groupby(by='vote')['imDbRatingVotes'].agg(stats.median).values)

        series = QHorizontalBarSeries()
        series.setLabelsVisible(True)
        series.append(set0)
        series.append(set1)

        self.chart = QChart()
        self.chart.addSeries(series)
        self.chart.setTitle("<span style='font-size: 12pt; font:Arial;'>Показатель оценивания популярных и непопулярных фильмов</span>")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.legend().setFont(QFont('Arial', 10))


        lst = map(lambda x: f'Оценка: {x}',self.full_frame.groupby(by='vote')['kinopoisk_votes'].agg(stats.median).index)
        categories = lst

        axis = QBarCategoryAxis()
        #axis.setLabelsAngle(-90)
        axis.append(categories)
        self.chart.createDefaultAxes()
        self.chart.setAxisY(axis, series)
        axis.setLabelsFont(QFont('Arial', 10))







