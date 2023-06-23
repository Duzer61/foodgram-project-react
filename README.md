
# Проект "Foodgram" - продуктовый помощник.

## Информация для ревью:
**Адрес проекта - https://foodgramophone.hopto.org
Администратор:
login - admin
password - mypass2023**

## 
Проект "Foodgram" предназначен для публикации рецептов приготовления различных блюд. "Foodgram" создан в качестве выпускного проекта курса [Python-разработчик](https://practicum.yandex.ru/backend-developer/) от [Яндекс.Практикум.](https://practicum.yandex.ru/)

### В проекте пользователи могут:

 регистрироваться на сайте
- добавлять свои рецепты с описанием количества необходимых ингредиентов
- редактировать свои рецепты
- просматривать рецепты других пользователей и добавлять их в избранное
- подписываться на других пользователей
- добавлять понравившиеся рецепты в корзину
- скачивать список покупок, который формируется из ингредиентов рецептов, добавленных в корзину
- незарегистрированные пользователи могут просматривать опубликованные рецепты

Администрирование реализовано в админ-панели Django.

## Запуск проекта с использованием CI/CD

На сервере устанавливаем Docker и Docker compose

    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
Проверить, что Docker заработал можно командой:

    systemctl status docker

В корне проекта создайте файл .env для хранения переменных окружения по такому шаблону, подставив ваши данные:

    POSTGRES_USER=your_username
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=django_db
    DB_HOST=db
    DB_PORT=5432
    DJANGO_KEY='your_secret_key'
	DEBUG=False
	ALLOWED_HOSTS=127.0.0.1, localhost, server_ip, your_host

На сервере создать директорию foodgram и скопировать в нее файлы .env и docker-compose.production.yml

На GitHub в репозитории проекта перейти в раздел `settings/secrets/actions` и создать **Actions secrets and variables** для проекта по шаблону:

    DB_HOST              db # название контейнера
    DB_PORT              5432 # порт для подключения к БД 
    HOST                 XXX.XXX.XXX.XXX # ip вашего сервера
    USER                 your_username # Имя пользователя для подключения к серверу
    SSH_KEY              # Приватный ключ доступа для подключению к серверу
    PASSPHRASE           # Серкретный пароль, если ваш ssh-ключ защищён паролем
    TELEGRAM_TO          # id Telegram-чата куда бот будет отправлять результат успешного выполнения
    TELEGRAM_TOKEN       # Токен бота Telegram для отправки уведомления
    DOCKER_USERNAME      # Имя пользователя Docker для публикации образов
    DOCKER_PASSWORD      # Пароль пользователя Docker

При пуше в ветку master на GitHub будет автоматически произведена сборка образов, пуш на DockerHub, развертывание и запуск контейнеров на сервере.

Дальше необходимо создать суперпользователя для развернутого проекта. Для этого в терминале подключиться к серверу и выполнить команду:

    sudo docker exec -it <id контейнера с бэкендом> python manage.py createsuperuser
можно также выполнить загрузку ингредиентов в базу данных командой:

    sudo docker exec -it <id контейнера с бэкендом> python manage.py load_data


## Технологии испльзованные в проекте
 - Python 3.9
 - Django 3.2.3
 - djangorestframework 3.14
 - Docker
 - Nginx
 - gunicorn
 - PostgreSQL
 - GitHub Actions


## Автор
Данил Кочетов - [GitHub](https://github.com/Duzer61)
Некоторое время рабочий проект будет размещен на https://foodgramophone.hopto.org