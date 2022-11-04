# Используемые библиотеки
import requests
from bs4 import BeautifulSoup
import csv
from time import sleep

# Заголовок HTTP-запроса
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0 "
}

# Процедура проверки: фильм или сериал?
def check(name):
    if "сериал" in name:
        return True
    else:
        return False

# Функция для сбора информации
def parser(user_id):
    proxy_counter = -1
    page_counter = 0
    proxy_constaint = 0
    # СОздать файл для записи результатов
    with open(f"C:\\Users\\Home PC\\Desktop\\Python\\VKR\\Parsing_dataset\\Users\\User_{user_id}.csv", "w", encoding="utf-8", newline='') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(("KP_id","film_name","vote","year")) # Записать названия признаков
        while True:  # Бесконечный цикл
            if proxy_constaint == 11: # Проверка на максимальное количество полных проходов по списку прокси
                break
            proxy_counter += 1
            rq = f"https://www.kinopoisk.ru/user/{user_id}/votes/list/ord/date/perpage/200/page/{page_counter}/#list"
            if proxy_counter == 11: # Если перебрали все прокси, то перебирать их заново
                proxy_constaint += 1
                proxy_counter = 0
            # Выполнить запрос
            response = requests.get(rq, headers=headers, proxies=proxies_list[proxy_counter])
            sleep(3) # Пауза 3 секунды
            if response.status_code == 404: # Если код уведомления 404, значит все страницы перебрали
                break
            else:
                soup = BeautifulSoup(response.text, "lxml")
                if soup.find("html")["prefix"] == "og: http://ogp.me/ns#": # Проверка на капчу
                    continue
                page_counter += 1 # Переход на следующую страницу
                buf = soup.find_all("div", class_="item")
                for i in buf:     # Цикл по всем фильмам на странице
                    # Поиск информации
                    name = i.find("div", class_="info").find("div", class_="nameRus").find("a").string
                    print(name)
                    vote = i.find("div", class_="vote").string
                    id = i.find("div", class_="info").find("div", class_="nameRus").find("a")["href"][6:-1]
                    year = i.find("div", class_="info").find("div", class_="nameRus").find("a").string[-5:-1]
                    if not vote is None: # Проверка наличия оценки у фильма
                        if check(name):  # Проверка на фильм
                            continue
                        else:
                            name = name[:-7]
                            print('Пишем: ',name)
                            a_pen.writerow((id, name, vote,year))
        return 'success'

# Список всех используемых прокси
proxies_list = [{
    "https": f'http://user80206:cwis5d@185.118.67.164:6419'
},
{
    "https": f'http://user80206:cwis5d@185.118.67.164:7402'
},
{
    "https": f'http://user80206:cwis5d@185.118.67.166:7630'
},
{
    "https": f'http://user80206:cwis5d@185.118.67.166:9615'
},
    {
        "https": f'http://user80206:cwis5d@185.118.67.171:3580'
    },

    {
        "https": f'http://user80206:cwis5d@185.118.67.171:5124'
    },

    {
        "https": f'http://user80206:cwis5d@185.118.67.176:3263'
    },
    {
        "https": f'http://user80206:cwis5d@185.118.67.176:9435'
    },
{
    "https": f'http://user80206:cwis5d@185.118.67.187:1676'
},
{
    "https": f'http://user80206:cwis5d@185.118.67.187:6003'
},
]

if __name__ == "__main__":
    parser("39431466")