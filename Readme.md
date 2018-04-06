## Отчет по тестовому заданию

Автотест был реализован на Python 3.6 и Robot Framework 3.0.2


### Состав решения

library - папка с библиотекой на python
config - папка с variables.py файлом переменных автотеста
aut - папка с тестирумым приложением
tests - папка с тестом
report - папка с отчетами теста

### Требования и зависимости

Для запуска тестового приложения требуется:

        Docker, Docker-compose

    В папке ./aut последовательно запустить команды для сборки
    docker-контейнера с тестируемым приложением:

        docker-compose build

        docker-compose up


Для запуска теста требуются:

        Python 3.6

    Установить зависимости при промощи команды:

        pip install -r requirements.txt

### Запуск автотеста

Запустите команду:

    robot -d report --variablefile config/variables.py tests

### Описание

Тестовые шаги автотеста реализованы по техническому заданию.

При выполнении команды docker build файл Clients.db загружается в docker-образ и
база данных на локальном диске в ходе выполнения теста не обновляется. Автотест
определяет такие ошибки.

Перечень ошибок с описанием:

    1) Добавление нового клиента и нового сервиса не отражается в базе данных
       docker-контейнера. Новый клиент добавляется в базу данных с пустым
       списком услуг. На Шаге 7 теста API возвращает данные со списком услуг
       и их количеством. Если, по истечении времени ожидания, количество услуг
       нового клиента осталось нулевым, выводится  сообщение о том, что
       клиента, возможно, нет в базе данных.

    2) На шаге 5 теста подключаяется новая услуга для клиента с положительным
       балансом. Данные о стоимости подключенной услуги фиксируются. На шаге 8
       автотест получает текущий баланс из базы данных на локальном диске.
       На шаге 9 расчитывается ожидаемый баланс клиента {начальный баланс} - {стоимость подключения услуги}
       и сравнивается с текущим балансом. Из-за того, что добавление данных происходит в базе
       данных docker-контейнера, а база данных на локальном диске остается без изменений,
       ожидаемый и текущий баланс не равны, возникает ошибка, выводится собщение.