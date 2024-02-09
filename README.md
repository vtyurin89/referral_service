
## RESTful API сервис для реферальной системы

#### Реферальная система, созданная с помощью Django REST Framework. Если вы нашли баг, пожалуйста, создайте Issue.


### Основные технологии
* Django REST Framework
* MySQL
* Simple JWT
* drf-yasg (Swagger generator)

### Для локальной установки
* $ git clone https://github.com/vtyurin89/referral_service.git
* $ cd referral_service
* $ pip install --user pipenv
* Установите переменные окружения или задайте переменные SECRET_KEY и MYSQL_PASSWORD в settings.py.
* $ python manage.py makemigrations
* $ python manage.py migrate

### Запуск сервиса
```
$ python manage.py runserver
```
### Тестирование
```
$ python manage.py test my_referrals
```