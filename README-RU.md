# Бот для [Clayton](https://alexell.ru/cc/clayton)

![img1](.github/images/demo.png)

> 🇺🇸 README in english available [here](README.md)

## Функционал
| Функция                                                        | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅       |
| Привязка прокси к сессии                                       |        ✅       |
| Автоматический фарминг                                         |        ✅       |
| Автоматические игры (Stack и 512)                              |        ✅       |
| Docker                                                         |        ✅       |

## [Настройки](https://github.com/Alexell/ClaytonBOT/blob/main/.env-example)
| Опция                   | Описание                                                                   |
|-------------------------|----------------------------------------------------------------------------|
| **API_ID / API_HASH**   | Данные платформы, с которой запускать сессию Telegram (сток - Android)     |
| **ERRORS_BEFORE_STOP**  | Количество неудачных запросов, по достижению которых, бот остановится      |
| **USE_PROXY_FROM_FILE** | Использовать-ли прокси из файла `bot/config/proxies.txt` (True / False)    |

**API_ID** и **API_HASH** вы можете получить после создания приложения на [my.telegram.org/apps](https://my.telegram.org/apps)

## Быстрый старт
### Windows
1. Убедитесь, что у вас установлен **Python 3.10** или более новая версия.
2. Используйте `INSTALL.bat` для установки, затем укажите ваши API_ID и API_HASH в .env
3. Используйте `START.bat` для запуска бота (или в консоли: `python main.py`)

### Linux
1. Клонируйте репозиторий: `git clone https://github.com/Alexell/ClaytonBOT.git && cd ClaytonBOT`
2. Выполните установку: `chmod +x INSTALL.sh START.sh && ./INSTALL.sh`, затем укажите ваши API_ID и API_HASH в .env
3. Используйте `./START.sh` для запуска бота (или в консоли: `python3 main.py`)

## Запуск в Docker
```
$ git clone https://github.com/Alexell/ClaytonBOT.git
$ cd ClaytonBOT
$ cp .env-example .env
$ nano .env # укажите ваши API_ID и API_HASH, остальное можно оставить по умолчанию
```
### Docker Compose (рекомендуется)
```
$ docker-compose run bot -a 1 # первый запуск для авторизации (переопределяем аргументы)
$ docker-compose start # запуск в фоновом режиме (аргументы по умолчанию: -a 2)
```
### Docker
```
$ docker build -t clayton_bot .
$ docker run --name ClaytonBOT -v .:/app -it clayton_bot -a 1 # первый запуск для авторизации
$ docker rm ClaytonBOT # удаляем контейнер для пересоздания с аргументами по умолчанию
$ docker run -d --restart unless-stopped --name ClaytonBOT -v .:/app clayton_bot # запуск в фоновом режиме (аргументы по умолчанию: -a 2)
```

## Ручная установка
Вы можете скачать [**Репозиторий**](https://github.com/Alexell/ClaytonBOT) клонированием на вашу систему и установкой необходимых зависимостей:
```
$ git clone https://github.com/Alexell/ClaytonBOT.git
$ cd ClaytonBOT

# Linux
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ cp .env-example .env
$ nano .env # укажите ваши API_ID и API_HASH, остальное можно оставить по умолчанию
$ python3 main.py

# Windows (сначала установите Python 3.10 или более новую версию)
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
> copy .env-example .env
> # укажите ваши API_ID и API_HASH, остальное можно оставить по умолчанию
> python main.py
```

Также для быстрого запуска вы можете использовать аргументы:
```
$ python3 main.py --action (1/2)
# или
$ python3 main.py -a (1/2)

# 1 - создать сессию
# 2 - запустить бот
```

## Запуск  бота в фоновом режиме (Linux)
```
$ cd ClaytonBOT

# с логированием
$ setsid venv/bin/python3 main.py --action 2 >> app.log 2>&1 &

# без логирования
$ setsid venv/bin/python3 main.py --action 2 > /dev/null 2>&1 &

# Теперь вы можете закрыть консоль и бот продолжит свою работу.
```

### Найти процесс бота
```
$ ps aux | grep "python3 main.py" | grep -v grep
```