import json
import logging
import os
import sys
import time
from logging.config import dictConfig
from pprint import pprint

from colorama import Fore, init
from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm, trange
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class Utils:

    @staticmethod
    def parse_url(url: str):
        last_part = url.split('/')[-1]
        return last_part.split('_')[1]

    @staticmethod
    def dump_json_into_file(obj: dict, file_name: str):
        with open(file_name, 'w') as outfile:
            json.dump(obj, outfile, indent=4)


driver = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
options = Options()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver.add_experimental_option("prefs", prefs)
driver.add_argument("headless")
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
              '%(asctime)-5s %(levelname)-8s %(message)s'}
    },
    handlers={
        'e': {'class': 'logging.FileHandler',
              'filename': 'error.log',
              'formatter': 'f',
              'level': logging.WARNING, },
    },
    root={
        'handlers': ['e'],
        'level': logging.WARNING,
    },
)

dictConfig(logging_config)

logger = logging.getLogger()
logger.debug('often makes a very good meal of %s', 'visiting tourists')


class TalkytimesScrapper:

    MAN_IDS = []
    MAN_URLS = {}
    MAN_IDS_SAVED = []

    def __init__(self, driver, login, password, history_file_name='man_history.json'):
        self.LOGIN = login
        self.PASSWORD = password
        self.history_file_name = LOGIN + '_' + history_file_name
        self.driver = driver
        self.message = 'Hello {name} {city} {age} {country}'
        self.recieve_history()
        self.interval = 40
        self.running = False
        self.creds_file_name = 'creds.json'
        self.scroll_anount = 1
        self.base_url = 'https://talkytimes.com/auth/login'

    def start(self):
        while self.running:
            try:
                print(Fore.WHITE + 'Запуск')
                if scrapper.driver.current_url == self.base_url:
                    self.login(True)
                self.recieve_history()
                time.sleep(2)
                self.enter_chat()
                time.sleep(2)
                self.page_refresh()
                time.sleep(2)
                self.come_to_online_saved_chat()
                self.scroll_chat_block()
                self.collect_chat_rooms_ids(True)
                time.sleep(1)
                self.come_to_online_ongoing_chat()
                self.page_refresh()
                time.sleep(1)
                self.scroll_chat_block()
                self.collect_chat_rooms_ids()
                pprint(self.MAN_URLS)
                time.sleep(2)
                self.process_man_ids()
                print(Fore.WHITE)
                print('Круг завершен ожидаю')
                for i in trange(self.interval):
                    time.sleep(1)
            except KeyboardInterrupt:
                print(Fore.RED + 'Остановлен сборщик данных')
                print(Fore.YELLOW + 'Не выключайте пока сохраняется история')
                self.running = False
                Utils.dump_json_into_file(
                    self.man_history, self.history_file_name)
                print(Fore.GREEN + 'Успешно сохранено перевожу в меню')
                time.sleep(2)
                self.main_menu()

    def main_menu(self):
        os.system('cls')
        print(Fore.WHITE)
        print('Введите 1 - для запуска программы')
        print('Введите 2 - для выхода из программы')
        print('Введите 3 - для проверки истории')
        print('Введите 4 - для очистки истории')
        print('Введите 5 - для того чтобы задать текущее сообщение')
        print('Введите 6 - для задания интервала')
        print('Введите 7 - для входа в аккаунт')

        action = input('Введите действие: ')
        if action == '1':
            self.running = True
            os.system('cls')
            self.start()
        elif action == '2':
            os.system('cls')
            print(Fore.RED + 'Выход из программы')
            self.driver.quit()
            sys.exit()
        elif action == '3':
            os.system('cls')
            self.show_history()
        elif action == '4':
            os.system('cls')
            self.clear_history()
        elif action == '5':
            os.system('cls')
            self.set_message()
        elif action == '6':
            os.system('cls')
            self.set_interval()
        elif action == '7':
            os.system('cls')
            self.login()
        else:
            print(Fore.RED + 'Неверный ввод')
            time.sleep(0.5)
            self.main_menu()

    def clear_history(self):
        print(Fore.RED + 'Вы уверены?')
        interval = input('1 если да, любой другой символ если нет: ')
        if interval == '1':
            self.man_history = {}
            Utils.dump_json_into_file(self.man_history, self.history_file_name)
        self.main_menu()

    def show_history(self):
        print(Fore.YELLOW + 'История прочитана')
        print(Fore.WHITE + 'История: ')
        pprint(self.man_history)
        time.sleep(2)
        self.main_menu()

    def set_message(self):
        print(Fore.YELLOW + 'Введите сообщение')
        print(Fore.WHITE + '''Поддерживаемые параметры
        {name} - Имя пользователя
        {city} - Город пользователя
        {age} - Возраст пользователя
        {country} - Страна пользователя
        ''')
        self.message = input('Введите сообщение: ')
        self.main_menu()

    def set_interval(self):
        print(Fore.YELLOW + 'Введите интервал в секундах ( по умолчанию - 40с )')
        interval = input('Введите интервал: ')
        self.interval = int(interval)
        self.main_menu()

    def recieve_history(self):
        if os.path.exists(self.history_file_name):
            self.f = open(self.history_file_name, 'r+', encoding='utf-8')
            self.man_history = json.load(self.f)
            self.f.close()
        else:
            self.f = open(self.history_file_name, 'w', encoding='utf-8')
            self.man_history = {}
            json.dump(self.man_history, self.f, indent=4)
            self.f.close()

    def input_login_creds(self):
        self.LOGIN = input('Введите логин: ')
        self.PASSWORD = input('Введите пароль: ')
        creds = {
            'login': self.LOGIN,
            'password': self.PASSWORD
        }
        Utils.dump_json_into_file(creds, self.creds_file_name)

    def get_login_creds_from_file(self):
        self.f = open(self.creds_file_name, 'r+', encoding='utf-8')
        self.creds = json.load(self.f)
        self.f.close()
        self.LOGIN = self.creds['login']
        self.PASSWORD = self.creds['password']

    def login(self, auto_load=False):
        print(Fore.YELLOW + 'Вход в аккаунт')
        self.driver.get(self.base_url)
        try:
            login_element = self.driver.find_element(
                by=By.XPATH,
                value="/html/body/div[1]/div/div[1]/main/div/div/div/div/div[1]/div/div[1]/form/div/div[1]/div/input")
            login_element.clear()
            login_element.send_keys(self.LOGIN)
            pass_element = self.driver.find_element(
                by=By.XPATH,
                value="/html/body/div[1]/div/div[1]/main/div/div/div/div/div[1]/div/div[1]/form/div/div[2]/div/input")
            pass_element.clear()
            pass_element.send_keys(self.PASSWORD)
            pass_element.send_keys(Keys.RETURN)
            print(Fore.YELLOW + f'Успешно вошли {self.LOGIN}')
        except NoSuchElementException as e:
            print(Fore.RED + f'Вход не успешен')
            logging.warning(f'{e} caught in login')
            pass
        except ElementNotInteractableException:
            logging.warning(f'{e} caught in login')
            print(Fore.RED + f'Вход не успешен')
            pass
        if not auto_load:
            self.main_menu()

    def get_profile_info(self, man_id: int) -> dict:
        print(Fore.YELLOW + f'Сбор информации с профиля {man_id}')
        self.driver.get(f'https://talkytimes.com/user/id/{man_id}')
        time.sleep(1)
        try:
            name_age_element = self.driver.find_element(
                by=By.CSS_SELECTOR,
                value='div.herProfile-info-name > span:nth-child(1)'
            )
            name, age = [el.strip()
                         for el in name_age_element.text.split(', ')]
            city_country_element = self.driver.find_element(
                by=By.CSS_SELECTOR,
                value='div.herProfile-info-location'
            )
            city, country = [el.strip()
                             for el in city_country_element.text.split(', ')]
            return {
                'name': name,
                'age': age,
                'city': city,
                'country': country
            }
        except NoSuchElementException as e:
            logging.warning(f'{e} caught in retrieve profile info')
            print(Fore.RED + f'Не найдена информация по профилю {man_id} {e}')
            return {}
        except ElementNotInteractableException:
            logging.warning(f'{e} caught in retrieve profile info')
            print(Fore.RED + f'Не найдена информация по профилю {man_id} {e}')
            return {}

    def check_previous_history(self, man_id: int) -> bool:
        if man_id in self.man_history.get(self.message.lower(), []):
            print(Fore.RED + 'Проверка на присутствие в истории - провалена')
            return False
        print(Fore.GREEN + 'Проверка на присутствие в истории - пройдена')
        return True

    def get_left_messages(self) -> bool:
        print(Fore.YELLOW + f'Проверка лимита оставшихся сообщений')
        time.sleep(1)
        try:
            notify_elem = self.driver.find_element(
                by=By.CLASS_NAME,
                value='scroll-button__text')
            if notify_elem.text == "You can't message users that show no activity":
                print(Fore.RED + 'Невозможно написать не активному пользователю')
                return False
            if notify_elem.text.strip().startswith('You have'):
                print(Fore.GREEN + 'Проверка на лимиты успешна')
                return True
            else:
                print(Fore.RED + 'Проверка на лимиты провалена')
                return False
        except NoSuchElementException as e:
            print(Fore.RED + 'Проверка на лимиты провалена')
            logging.warning(f'{e} caught in left messages retrieve')
            return False
        except ElementNotInteractableException:
            print(Fore.RED + 'Проверка на лимиты провалена')
            logging.warning(f'{e} caught in left messages retrieve')
            return False

    def page_refresh(self):
        print(Fore.YELLOW + 'Обновление страницы')
        driver.refresh()
        self.toggle_online()

    def check_saved(self, man_id: str):
        if man_id in self.MAN_IDS_SAVED:
            print(Fore.RED + 'Проверка на отсутствие в разделе saved - провалена')
            return False
        print(Fore.GREEN + 'Проверка на отсутствие в разделе saved - пройдена')
        return True

    def clear(self):
        print(Fore.YELLOW + 'Очистка сохраненной информации')
        self.MAN_IDS = []
        self.MAN_IDS_SAVED = []
        self.MAN_URLS = {}

    def filter_saved_ids(self):
        print(Fore.YELLOW + 'Фильтрация сохраненных id')
        elements = []
        for ind, el in zip(tqdm(self.MAN_IDS), self.MAN_IDS):
            if el in self.MAN_IDS_SAVED:
                elements.append(el)
        for ind, el in zip(tqdm(elements), elements):
            try:
                self.MAN_IDS.remove(el)
                del self.MAN_URLS[el]
            except Exception as e:
                logging.warning(f'{e} caught in left filtering saved ids')

    def man_complete_check(self, man_id: str) -> bool:
        print(Fore.YELLOW + f'Проверка условий по профилю {man_id}')
        self.driver.get(self.MAN_URLS[man_id])
        time.sleep(2)
        if not self.check_previous_history(man_id):
            print(Fore.RED + f'Проверка профиля {man_id} - провалена')
            return False
        if not self.check_saved(man_id):
            print(Fore.RED + f'Проверка профиля {man_id} - провалена')
            return False
        if not self.get_left_messages():
            print(Fore.RED + f'Проверка профиля {man_id} - провалена')
            return False
        print(Fore.GREEN + f'Проверка профиля {man_id} - успешна')
        return True

    def come_to_online_ongoing_chat(self):
        print(Fore.YELLOW + f'Вход в раздел ongoing')
        try:
            self.driver.find_element(
                by=By.CSS_SELECTOR,
                value='body > div.main-app-content > div > div.page > main > div > div > div.col-9 > div > div.dialogs-page-wrapper > div > div.users_wrap > div > div:nth-child(1) > div.filter.s-p-x-1 > button:nth-child(1)'
            ).click()
            time.sleep(1)
        except NoSuchElementException as e:
            print(
                Fore.RED + 'Не получилось войти в раздел ongoing, обратитесь к администратору')
            logging.warning(f'{e} caught in come_to_online_ongoing_chat')
            pass
        except ElementNotInteractableException as e:
            print(
                Fore.RED + 'Не получилось войти в раздел ongoing, обратитесь к администратору')
            logging.warning(f'{e} caught in come_to_online_ongoing_chat')
            pass

    def come_to_online_saved_chat(self):
        print(Fore.YELLOW + f'Вход в раздел saved')
        try:
            self.driver.find_element(
                by=By.CSS_SELECTOR,
                value='body > div.main-app-content > div > div.page > main > div > div > div.col-9 > div > div.dialogs-page-wrapper > div > div.users_wrap > div > div:nth-child(1) > div.filter.s-p-x-1 > button:nth-child(2)'
            ).click()
            time.sleep(1)
        except NoSuchElementException:
            print(
                Fore.RED + 'Не получилось войти в раздел saved, обратитесь к администратору')
            logging.warning(f'{e} caught in come_to_online_saved_chat')
            pass
        except ElementNotInteractableException as e:
            print(
                Fore.RED + 'Не получилось войти в раздел saved, обратитесь к администратору')
            logging.warning(f'{e} caught in come_to_online_saved_chat')
            pass

    def enter_chat(self):
        print(Fore.YELLOW + f'Вход в чат')
        try:
            self.driver.find_element(
                by=By.XPATH,
                value='/html/body/div[1]/div/div[1]/header/div/div/div[2]/div[2]/a').click()
            time.sleep(1)
            print(Fore.GREEN + 'Вход в аккаунт успешен')
        except NoSuchElementException as e:
            print(
                Fore.RED + 'Не получилось войти в чат, обратитесь к администратору')
            logging.warning(f'{e} caught in enter_chat')
            pass
        except ElementNotInteractableException as e:
            print(
                Fore.RED + 'Не получилось войти в чат, обратитесь к администратору')
            logging.warning(f'{e} caught in enter_chat')
            pass

    def toggle_online(self):
        print(Fore.YELLOW + f'Переключение на online')
        for i in trange(10):
            time.sleep(1)
            print(Fore.WHITE +
                  f'Попытка переключить онлайн бар {i+1} осталось {10-(i+1)} попыток')
            try:
                self.driver.find_element(
                    by=By.CLASS_NAME,
                    value='chat-online-item').click()
                i = 10
                print(Fore.GREEN + 'Успешно включен онлайн бар')
                break
            except NoSuchElementException as e:
                print(
                    Fore.RED + 'Не получилось включить онлайн бар, обратитесь к администратору')
                logging.warning(f'{e} caught in toggle_online')
                pass
            except ElementNotInteractableException as e:
                print(
                    Fore.RED + 'Не получилось включить онлайн бар, обратитесь к администратору')
                logging.warning(f'{e} caught in toggle_online')
                pass

    def scroll_chat_block(self):
        print(Fore.YELLOW + 'Прокрутка чата')
        print(Fore.WHITE)
        for _ in trange(self.scroll_anount):
            try:
                self.driver.execute_script(
                    '''var obj = document.querySelector('.list-infinite');obj.scrollTop = obj.scrollHeight;''')
                time.sleep(3)
            except NoSuchElementException as e:
                print(
                    Fore.RED + 'Не получилось прокрутить чат, обратитесь к администратору')
                logging.warning(f'{e} caught in scroll_chat_block')
                pass
            except ElementNotInteractableException as e:
                print(
                    Fore.RED + 'Не получилось прокрутить чат, обратитесь к администратору')
                logging.warning(f'{e} caught in scroll_chat_block')
                pass

    def collect_chat_rooms_ids(self, saved=False):
        print(Fore.YELLOW + 'Сбор идентификаторов чатов')
        try:
            chat_rooms = self.driver.find_elements(by=By.CLASS_NAME,
                                                   value='dialog-item')

            for _, chat_room in zip(tqdm(chat_rooms), chat_rooms):
                chat_room.click()
                url = self.driver.current_url
                man_id = Utils.parse_url(url)
                if saved:
                    self.MAN_IDS_SAVED.append(man_id)
                else:
                    if not man_id in self.MAN_IDS_SAVED:
                        self.MAN_IDS.append(man_id)
                        self.MAN_URLS[man_id] = url
            time.sleep(1)
            if saved:
                print(Fore.WHITE + "Превью" + Fore.GREEN + ' saved ' +
                      Fore.WHITE + "онлайн идентификаторов")
                pprint(self.MAN_IDS_SAVED)
            else:
                print(Fore.WHITE + "Превью" + Fore.GREEN + ' ongoing ' +
                      Fore.WHITE + "онлайн идентификаторов")
                pprint(self.MAN_IDS)
        except NoSuchElementException as e:
            print(Fore.RED + f"Не получилось собрать айди из раздела {'saved' if saved else 'ongoing'} " +
                  f"из-за {e} обратитесь к администратору")
            logging.warning(f'{e} caught in collect_chat_rooms_ids')
            pass
        except ElementNotInteractableException as e:
            print(Fore.RED + f"Не получилось собрать айди из раздела {'saved' if saved else 'ongoing'} " +
                  f"из-за {e} обратитесь к администратору")
            logging.warning(f'{e} caught in collect_chat_rooms_ids')
            pass

    def send_message_in_dialog(self, url: str, message: str):
        print(Fore.WHITE + 'Отправка сообщения' + Fore.GREEN +
              f' {message}' + Fore.WHITE + f' по ссылке {url}')
        try:
            self.driver.get(url)
            man_id = Utils.parse_url(url)
            time.sleep(2)
            text_input_element = self.driver.find_element(
                by=By.CLASS_NAME,
                value='ui-textarea_control'
            )
            text_input_element.send_keys(message)
            text_input_element.send_keys(Keys.ENTER)

            # Input message
            # btn_element = self.driver.find_element(
            #     by=By.CSS_SELECTOR,
            #     value='button.ui-button.ui-button__size-xl.ui-button__type-primary.ui-button__icon-position-right'
            # )
            # btn_element.click()
            if not self.man_history.get(self.message.lower()):
                self.man_history[self.message.lower()] = [man_id]
            else:
                self.man_history[self.message.lower()
                                 ].append(man_id)
            print(Fore.GREEN + 'Успешно отправлено сообщение: ' + message)
            time.sleep(1)
        except NoSuchElementException as e:
            print(Fore.RED + f"Не получилось отправить сообщение" +
                  f"из-за {e} обратитесь к администратору")
            logging.warning(f'{e} caught in collect_chat_rooms_ids')
            pass
        except ElementNotInteractableException:
            print(Fore.RED + f"Не получилось отправить сообщение" +
                  f"из-за {e} обратитесь к администратору")
            logging.warning(f'{e} caught in collect_chat_rooms_ids')
            pass

    def process_man_ids(self):
        print(Fore.YELLOW + 'Проверка мужских идентификаторов')
        self.filter_saved_ids()
        for _, man_id in zip(tqdm(self.MAN_IDS), self.MAN_IDS):
            if not self.man_complete_check(man_id):
                continue
            if not ('{name}' not in self.message and '{city}' not in self.message and
                    '{country}' not in self.message and '{age}' not in self.message):
                man_profile_dict = self.get_profile_info(man_id)
                print(Fore.WHITE +
                      f'Получена информация {man_profile_dict} по id {man_id}')
            else:
                man_profile_dict = {}
            try:
                processed_message = self.message.format(**man_profile_dict)
            except KeyError as e:
                print(Fore.RED +
                      f'Не получена параметр профиля {e}... пропускаю ')
                continue
            print(Fore.GREEN + f'Итоговое сообщение {processed_message}')
            self.send_message_in_dialog(
                self.MAN_URLS[man_id], processed_message)
            time.sleep(2)
        Utils.dump_json_into_file(self.man_history, self.history_file_name)


if __name__ == '__main__':
    init()
    LOGIN = input('Введите логин: ')
    PASSWORD = input('Введите пароль: ')
    scrapper = TalkytimesScrapper(driver, login=LOGIN, password=PASSWORD)
    scrapper.driver.get(scrapper.base_url)
    if scrapper.driver.current_url == scrapper.base_url:
        scrapper.main_menu()
