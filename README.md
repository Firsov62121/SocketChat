# Чат на сокетах

# Как всё это запустить у себя
1) В .env файле прописываем нужные host и port сервера.
2) Запускаем сервер: python3 ./server.py
4) Запускаем клиентов: python3 ./client.py

# Интерфейс:
1) Поле для ввода имени отправляется при нажатии Enter-а
2) Поля для ввода сообщения отправляется при нажатии Enter-а или кнопки отправить.

# Замечания:
1) Большие сообщения не поддерживаются. Нет нормального разделения потока данных на малые. (Но можно увеличить размер читаемого буфера на клиенте и сервере через соответствующие параметры .env файла)
2) Нет отлавливания закрытия сервера при работе клиента.
3) Никакие БД для сохранения чата не используются, нет нормальной авторизации
4) Проект учебный, просто 'потрогать' сокеты.