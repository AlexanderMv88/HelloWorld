import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from urllib.parse import unquote



# Простой класс Task
class Task():
    # Поле id класса Task
    id = 0
    # Поле title класса Task
    title = ''
    # Поле description класса Task
    description = ''
    # Поле users класса Task. Т.к. задача может быть видна сразу нескольким пользователям поэтому использую массив
    users = []
    # Поле done класса Task
    done = False;

    # Конструктор класса Task
    def __init__(self, id, title, description, users, done):
        self.id = id
        self.title = title
        self.description = description
        self.users = users
        self.done = done

    # Преобразую в json
    def toJSON(self):
        ### Сначала преобразую массив пользователей в массив json-ов
        jsonUsers = []
        for ob in self.users:
            jsonUsers.append(ob.toJSON())
        ####
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
             # Подставляю массив json-ов как значение поля
            'users': jsonUsers,
            'done': self.done
        }



# Простой класс User
class User():
    # Поле id класса User
    id = 0
    # Поле name класса User
    name = ''

    # Конструктор класса User
    def __init__(self, id, name):
        self.id = id
        self.name = name
    # Преобразую в json
    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name
        }


# Класс отвечающий за обработку http запросов
class S(BaseHTTPRequestHandler):
    # Метод класса отвечающий за формирование кода ответа и его заголовков
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # Метод класса отвечающий за обработку GET запросов
    def do_GET(self):
        # Создаю тестовых пользователей в функции initUsers() и возвращаю их в переменную users
        users = self.initUsers()
        # Создаю задачи для тестовых пользователей в функции initTasks() c параметром users и возвращаю созданые задачи в переменную tasks
        tasks = self.initTasks(users)

        # Если путь до ресурса начинается с /user/
        if self.path.startswith('/user/'):
            # Достаю путь
            path = self.path
            # Декодирую кириллические символы
            path = unquote(path)
            # Достаю переменную из пути и преобразую в int
            idFromRequest = int(path[6:])
            # Фильтрую список по id
            fu = [x for x in users if x.id == idFromRequest]
            # Пустую переменную создал тут чтобы она была в зоне видимости кода
            n = ''
            # Если отфильтрованый список > 0
            if (len(fu) > 0):
                # Достаю первый элемент
                u=fu.__getitem__(0)
                # Сериализую в json
                n = json.dumps(u.toJSON())
            # Подставляю в ответ код и заголовки
            self._set_response()
            # Подставляю в тело json или ''
            self.wfile.write(n.encode('utf-8'), )
        # Если путь до ресурса == /users
        elif self.path == '/users':
            # Сериализую в json весь список
            jsonStr = json.dumps([ob.toJSON() for ob in users])
            # Подставляю в ответ код и заголовки
            self._set_response()
            # Подставляю в тело json
            self.wfile.write(jsonStr.encode('utf-8'), )
            # Если путь до ресурса == /users
        elif self.path == '/tasks':
            # Сериализую в json весь список
            jsonStr = json.dumps([ob.toJSON() for ob in tasks])
            # Подставляю в ответ код и заголовки
            self._set_response()
            # Подставляю в тело json
            self.wfile.write(jsonStr.encode('utf-8'), )
        else:
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            self._set_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'), )



    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    # Создаю тестовых пользователей и возвращаю их
    def initUsers(self):
        # Список пользователей
        users = []
        # Добавляю в список пользователей нового пользователя с именем Вася
        users.append(User(1, 'Вася'))
        users.append(User(2, 'Коля'))
        return users

    def initTasks(self, users):
        # Список задач
        tasks = []
        # Добавляю в список задач новую задачу с первым пользователем из массива users
        tasks.append(Task(1, 'Некий заголовок1', 'Тут описание1', [users[0]], False))
        tasks.append(Task(2, 'Некий заголовок2', 'Тут описание2', [users[1]], True))
        tasks.append(Task(3, 'Заголовок общей задачи', 'Описание общей задачи', users, False))
        return tasks



# Метод для запуска сервера где handler_class - это класс обработчик запросов
def run(server_class=HTTPServer, handler_class=S, port=8080):
    # Выставляю уровень логирования
    logging.basicConfig(level=logging.INFO)
    # Формирую адрес сервера с портом
    server_address = ('', port)
    # Создаю сервер с указанием сервера и класса обработчика
    httpd = server_class(server_address, handler_class)
    # Вывожу в лог сообщение
    logging.info('Starting httpd...\n')
    try:
        # Запускаю сервер
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


# Главный метод
if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        # Запускает сервер на опредленном порту
        run(port=int(argv[1]))
    else:
        # Запускает сервер на порту указанном в коде
        run()