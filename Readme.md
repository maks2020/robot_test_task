## Отчет по тестовому заданию

Автотест был реализован на Python 3.6 и Robot Framework 3.0.2


### Состав решения

library - папка с библиотекой на python
config - папка с variables.py файлом переменных автотеста
sut - папка с тестирумым приложением
tests - папка с тестом
report - папка с отчетами теста

### Требования и зависимости

Для запуска теста требуются:

    Docker, Docker-compose

    Python 3.6

Установить зависимости при промощи команды:

    pip install -r requirements.txt

В папке ./sut последовательно запустить команды для сборки
docker-контейнера с тестируемым приложением:

    docker-compose build

    docker-compose up

### Запуск автотеста

Запустите команду:

    robot -d report tests