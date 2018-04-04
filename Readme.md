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

### Описание

Тестовые шаги автотеста реализованы по техническому заданию.

При выполнении команды docker build файл Clients.db загружается в docker-образ и база данных на
локальном диске при работе API не обновляется. Автотест обрабатывает разницу в хранимых данных.

Обработка ошибок:

    1) Добавление нового клиента и нового сервиса не отражается в базе данных docker-контейнера.
       На Шаге 7  API возвращает данные с нулевым значением количества услуг. После завершения
       времени ожидания, вызывается сообщение о том, что клиента, возможно, нет в базе данных.

    2) Несоответсвие текущего значения баланса клиента рассчетному сопровождается сообщением
       об ошибке.
