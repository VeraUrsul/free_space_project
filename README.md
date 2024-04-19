## Описание проекта

Free Space - социальная сеть, где ты можешь делиться всем что тебе нравится ;)

Возможности на плаформе:
- публиковать посты с картинками
- добавлять посты в тематическую группу
- лайкать понравившиеся посты
- подписываться на любимых авторов
- добавлять посты в раздел Избранное

### Технологии

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

- Реализована авторизация и регистрация, используется пагинация.

### 1. Клонирование кода приложения с GitHub на сервер
```

git clone git@github.com:VeraUrsul/free_space_project.git

```
### 2. Создание и активация виртуального окружения
```

# Переходим в директорию backend-приложения проекта.
cd free_space_project/
# Создаём виртуальное окружение.
python -m venv venv
# Активируем виртуальное окружение.
# для Linux
source venv/bin/activate
# для Windows
source venv/Scripts/activate

```

### 3. Устанавливаем зависимости и применяем миграции
```
# Обновить пакет pip
python -m pip install --upgrade pip
# Устанавливаем зависимости
pip install -r requirements.txt
# Обновляем файл зависимостей
pip freeze > requirements.txt
# Применяем миграции.
python manage.py migrate

```

## 4. Создание и заполнение файла .env

```

touch .env
nano .env

```

## 5. Запускаем приложение

```

 python manage.py runserver

 ```

## Автор [Урсул Вера](https://github.com/VeraUrsul)
