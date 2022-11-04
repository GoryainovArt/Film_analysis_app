import smtplib
from email.mime.text import MIMEText
from random import randint

def send_mail(message,email):
    sender = "notifications.msd@gmail.com"
    password = "gkp221174"
    print(1)

    server =smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    print(2)

    try:
        server.login(sender,password)
        msg = MIMEText(message)
        msg['Subject'] = "Код подтверждения"
        server.sendmail(sender,email, msg.as_string())
        #server.sendmail(sender, "real.65432121@yandex.ru", f"Subject: Подтверждение регистрации{message}")
        return 'Successfully'
    except Exception as Ex:
        return f"Ошибка: {Ex}"

def main():
    message = str(randint(100000,1000000))
    print(0)
    print(send_mail(message,"real.65432121@yandex.ru"))

if __name__=="__main__":
    main()