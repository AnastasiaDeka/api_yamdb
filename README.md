# Follow API

## Описание

Проект YaMDb — это система для сбора отзывов пользователей на произведения в разных категориях (например, книги, фильмы, музыка). В проекте пользователи могут оставлять отзывы и комментарии, а также оценивать произведения.
Проект YaMDb не хранит сами произведения, но предоставляет возможность пользователям оставлять отзывы на них. Произведения могут быть отнесены к разным категориям (например, "Фильмы", "Книги", "Музыка"). Каждый отзыв может содержать текст и оценку произведения. Оценки пользователей формируют общий рейтинг произведения.

Кроме того, пользователи могут оставлять комментарии к отзывам, а доступ к различным функциям системы зависит от их роли.

## Ресурсы API

>**auth**

Аутентификация пользователей через JWT-токен.

>**users**

Управление пользователями, их данными и ролями.

>**titles**

Произведения (книги, фильмы, музыка и др.), на которые оставляются отзывы.

>**categories**

Категории произведений, такие как «Книги», «Фильмы», «Музыка».

>**genres**

Жанры произведений, к которым могут быть привязаны произведения.

>**reviews**

Отзывы пользователей на произведения.

>**comments**

Комментарии пользователей к отзывам.


Каждый из этих ресурсов доступен через API с использованием различных HTTP-методов и требует определённых прав доступа.

## Пользовательские роли и права доступа

Аноним — может просматривать произведения, читать отзывы и комментарии.
Аутентифицированный пользователь — может публиковать отзывы, ставить оценки, комментировать, редактировать и удалять свои отзывы и комментарии.
Модератор — имеет права аутентифицированного пользователя плюс возможность редактировать и удалять любые отзывы и комментарии.
Администратор — имеет полные права на управление контентом (создание и удаление произведений, категорий и жанров, назначение ролей пользователям).
Функциональность
Регистрация пользователей: Пользователь может зарегистрироваться с помощью email и username, получить токен для дальнейшей работы с API.
Добавление данных: Администратор может добавлять произведения, категории, жанры и управлять пользователями.
Отзывы и комментарии: Аутентифицированные пользователи могут оставлять отзывы и комментарии, редактировать и удалять их.
Токены для аутентификации: Все запросы к API, требующие аутентификации, должны сопровождаться JWT-токеном.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yourusername/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```
На macOS/Linux:
```
source venv/bin/activate
```
На Windows:
```
venv\Scripts\activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```


## Документация к API

После запуска dev-сервера документация к API будет доступна по адресу:
http://127.0.0.1:8000/redoc/

Документация описывает, как должен работать ваш API и какие запросы можно отправлять.
Документация представлена в формате Redoc.

## Примеры запросов

### Получение списка всех постов

>Статус 200 - удачное выполнение запроса

``` json
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "author": "N@uSABZwvzB2hGI0XPyqWoKuypfUWRM6iow_vAKLzkBRWc5UW4tg064HNpm8G@7TluCu@0bI43d6eyUuKABc",
      "text": "string",
      "pub_date": "2024-11-29T16:04:48.701Z",
      "image": "string",
      "group": 0
    }
  ]
}
```

### Cоздания нового поста с передачей данных

>Статус 201 - удачное выполнение запроса

``` json
{
  "text": "string",
  "group": 0
}

```

## Авторы:

Декаапольцева Анастасия

Кузнецова Екатерина

Баукова Людмила
