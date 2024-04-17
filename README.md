## Описание проекта



## Разворачиваем проект на удаленном сервере

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

## Создание и заполнение файла .env

```

touch .env
nano .env