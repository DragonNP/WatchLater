import json
from const_variables import *


class UsersDB:
    logger = logging.getLogger('user_db')

    def __init__(self):
        self.db = {}
        self.logger.setLevel(GLOBAL_LOGGER_LEVEL)
        self.logger.debug('Инициализация базы данных пользователей')

        self.location = os.path.expanduser(PATH_TO_USERS_DATA_BASE)
        self.load(self.location)

    def load(self, location):
        self.logger.debug('Загрузка базы данных')

        if os.path.exists(location):
            self.__load()
        return True

    def __load(self):
        self.logger.debug('Загрузка базы данных из файлв')
        self.db = json.load(open(self.location, 'r'))

    def __check_user(self, user_id: int):
        res = str(user_id) in self.db.keys()
        self.logger.debug(f'Проверка пользователе в базе данных. результат:{res}')
        return res

    def __dump_db(self):

        self.logger.debug('Сохранение базы данных в файл')
        try:
            json.dump(self.db, open(self.location, 'w+'))
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def add_user(self, user_id):
        self.logger.debug(f'Создание пользователя. id пользователя:{user_id}')

        try:
            if self.__check_user(user_id):
                self.logger.debug(f'Пользователь уже создан. id пользователя:{user_id}')
                return False

            self.db[str(user_id)] = {}
            self.__dump_db()
            return True
        except Exception as e:
            self.logger.error(f'Не удалось сохранить пользователя. id пользователя:{user_id}', e)
            return False

    def get_list(self, user_id: int):
        self.logger.debug(
            f'Запрос на получение списка. id пользователя:{user_id}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)

            return self.db[str(user_id)]
        except Exception as e:
            self.logger.error(
                f'Не удалось получить список. id пользователя:{user_id}', e)
            return {}

    def add_link(self, user_id: int, link: str, name: str):
        self.logger.debug(f'Добавление ссылки. id пользователя:{user_id}, ссылка:{link}, имя:{name}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)

            if name in self.db[str(user_id)]:
                return False, 'Название совпадает с уже добавленной ссылкой'

            self.db[str(user_id)][name] = link
            self.__dump_db()
            return True, ''
        except Exception as e:
            self.logger.error(f'Не удалось сохранить ссылку. id пользователя:{user_id}, ссылка:{link}, имя:{name}', e)
            return False, ''

    def check_link(self, user_id: int, name: str):
        res = name in self.db[str(user_id)]
        self.logger.debug(f'Проверка ссылки в базе данных. результат:{res}')
        return res

    def remove_link(self, user_id: int, name: str):
        self.logger.debug(f'Удаление ссылки. id пользователя:{user_id}, имя:{name}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)
            if not self.check_link(user_id, name):
                self.logger.debug(f'Ссылка не найдена не найдена. id пользователя:{user_id}, имя:{name}')
                return False

            del self.db[str(user_id)][name]
            self.__dump_db()
            return True
        except Exception as e:
            self.logger.error(f'Не удалось удалить ссылку. id пользователя:{user_id}, имя:{name}', e)
            return False

    def remove_all(self, user_id: int):
        self.logger.debug(f'Удаление всех ссылок. id пользователя:{user_id}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)
                return True

            self.db[str(user_id)] = {}
            self.__dump_db()
            return True
        except Exception as e:
            self.logger.error(f'Не удалось все ссылки. id пользователя:{user_id}', e)
            return False
