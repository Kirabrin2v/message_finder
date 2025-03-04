import os
import re
import configparser
import colorama
from colorama import Fore, Back, Style, init
from string import Template

init(autoreset=True)

config = configparser.ConfigParser()
config.read('settings.ini', encoding="UTF-8") 

#Регулярные выражения
reg_nickname = r'([А-яA-Za-z0-9~!@#$^*\-_=+ёЁ]{1,16})'
reg_prefixs = r'(.{1,30}?\[[А-я]{5,20}\].{1,5}?)'
reg_time = r'\[([0-9]{2}:[0-9]{2}:[0-9]{2})\]'
reg_type_chat = r'(?:\[(Лк|Гл)\]){0,1}'
reg_mods_info = r'(?:[^\[\]]){1,30}'
reg_logs_info = r' \[Client thread\/INFO\]: \[CHAT\] '
reg_message = r'(.{1,256})'

#Шаблоны вывода сообщений. Можно отредактировать в settings.ini
pattern_mode_selection = config["VARIABLES"]["pattern_mode_selection"]
if pattern_mode_selection.lower() == "default":
    pattern_mode_selection = "${LIGHTCYAN}Режимы работы:\n\
${WHITE}Поиск переписки с определёным человеком -${RED} 1\n\
${WHITE}Поиск всех, с кем велась переписка -${RED} 2\n\
${WHITE}Поиск сообщений в общем чате -${RED} 3\n\
${WHITE}Поиск ников всех игроков, которые писали в чат -${RED} 4\n\
${LIGHTCYAN}Ввод: ${WHITE}"
pattern_mode_selection = Template(pattern_mode_selection)

pattern_i_send = config["VARIABLES"]["pattern_i_send"]
if pattern_i_send.lower() == "default":
    pattern_i_send = "[${time}] [${LIGHTBLACK}Я ${WHITE}-> ${RED}${nickname}${WHITE}] ${LIGHTYELLOW}${message}"
pattern_i_send = Template(pattern_i_send)

pattern_me_send = config["VARIABLES"]["pattern_me_send"]
if pattern_me_send.lower() == "default":
    pattern_me_send = "[${time}] [${RED}${nickname} ${WHITE}-> ${LIGHTBLACK}Мне${WHITE}] ${LIGHTYELLOW}${message}"
pattern_me_send = Template(pattern_me_send)

pattern_general_chat = config["VARIABLES"]["pattern_general_chat"]
if pattern_general_chat.lower() == "default":
    pattern_general_chat = "[${time}] [${type_chat}] ${prefixs}${RED}${nickname}${WHITE}: ${LIGHTYELLOW}${message}"
pattern_general_chat = Template(pattern_general_chat)
#f"{time_now} {type_chat} {prefixs}{Fore.RED}{match_nick}{Fore.WHITE}: {Fore.LIGHTYELLOW_EX}{message}\n"

#Словарь для замены конструкций на более простые и создания шаблонов с переменными до их объявления
comparison = {"BLACK": Fore.BLACK, "BLUE": Fore.BLUE, "CYAN": Fore.CYAN, "GREEN": Fore.GREEN, "LIGHTBLACK": Fore.LIGHTBLACK_EX, "LIGHTBLUE": Fore.LIGHTBLUE_EX, "LIGHTCYAN": Fore.LIGHTCYAN_EX,
              "LIGHTGREEN": Fore.LIGHTGREEN_EX, "LIGHTMAGENTA": Fore.LIGHTMAGENTA_EX, "LIGHTRED": Fore.LIGHTRED_EX, "LIGHTWHITE": Fore.LIGHTWHITE_EX, "LIGHTYELLOW": Fore.LIGHTYELLOW_EX,
              "MAGENTA": Fore.MAGENTA, "RED": Fore.RED, "RESET": Fore.RESET, "WHITE": Fore.WHITE}
              
              

file_path = config["VARIABLES"]["path_to_log_file"]
if file_path.lower() == "default":
    file_path = os.path.normpath(os.getcwd() + os.sep + os.pardir) + os.sep + "logs" + os.sep + "latest.log"
    print(file_path)
try:
    with open(file_path, "r", encoding="UTF-8") as f:
        all_str = f.readlines()
        
except UnicodeDecodeError:
    with open(file_path, "r") as f:
        all_str = f.readlines()
    #print(f"[{Fore.RED}WARNING{Fore.WHITE}]Для корректного отображения всех символов измените кодировку файла логов на UTF-8\n")
    print(f"[{Fore.RED}WARNING{Fore.WHITE}]Для корректного отображения всех символов пропишите в параметрах запуска Вашего Майнкрафт-лаунчера следующую строку: \"-Dfile.encoding = UTF-8\" без кавычек\n")
    
except FileNotFoundError:
    answ = input(f"[{Fore.RED}WARNING{Fore.WHITE}]Неверно введён путь к файлу. Чтобы использовать путь по умолчанию, введите \"1\". Если уже используется путь по умолчанию, введите в settings.ini полный путь до файла с логами.\nВвод: ")
    if answ == "1":
        config["VARIABLES"]["path_to_log_file"] = "default"

    else:
        config["VARIABLES"]["path_to_log_file"] = answ

    with open('settings.ini', 'w') as configfile:
            config.write(configfile)
    exit()
    
while True:
    mode_work = int(input(pattern_mode_selection.substitute(**comparison)))
    
    if mode_work in [1, 2]:
        if mode_work == 1:
            nick = input("Ник игрока, переписку с которым нужно просмотреть:\n")
            print()
        else:
            nick = None
            nicks = set()

        for string in all_str:
            
            match_i_send =  re.search(reg_time + reg_logs_info + reg_mods_info + r"\[Я -> " + reg_nickname + r"\] " + reg_message , string)
            match_me_send = re.search(reg_time + reg_logs_info + reg_mods_info + r"\[" + reg_nickname + r" -> Мне\] " + reg_message, string)
                
            if match_i_send:
                time_now = match_i_send.group(1)
                match_nick = match_i_send.group(2)
                message = match_i_send.group(3)
                comparison["time"] = time_now
                comparison["nickname"] = match_nick
                comparison["message"] = message
                if mode_work == 1:
                    if nick.lower() == match_nick.lower():
                        #print(f"[{time_now}] [{Fore.LIGHTBLACK_EX}Я {Fore.WHITE}-> {Fore.RED}{match_nick}{Fore.WHITE}]{Fore.LIGHTYELLOW_EX} {message}\n")
                        print(pattern_i_send.substitute(**comparison) + "\n")
                elif mode_work == 2:
                    nicks.add(match_nick)
                        
            elif match_me_send:
                time_now = match_me_send.group(1)
                match_nick = match_me_send.group(2)
                message = match_me_send.group(3)
                comparison["time"] = time_now
                comparison["nickname"] = match_nick
                comparison["message"] = message
                if mode_work == 1:
                    if nick.lower() == match_nick.lower():
                        #print(f"[{time_now}] [{Fore.RED}{match_nick} {Fore.WHITE}-> {Fore.LIGHTBLACK_EX}Мне{Fore.WHITE}]{Fore.LIGHTYELLOW_EX} {message}\n")
                        print(pattern_me_send.substitute(**comparison) + "\n")
                else:
                    nicks.add(match_nick)

        if mode_work == 2:
            for nick in nicks:
                print()
                print(Fore.RED + nick)
            print()
            
    elif mode_work == 3:
        nicks = []
        number = int(input("Сколько ников Вы хотите ввести?\n"))
        for i in range(number):
            nick = input("Введите ник игрока № " + str(i+1) + "\n")
            print()
            nicks.append(nick)
    
        for string in all_str:
            for nick in nicks:
                match = re.search('^' + reg_time + reg_logs_info + reg_mods_info + reg_type_chat + reg_prefixs + reg_nickname + ': ' + reg_message, string)
                if match:
                    match_nick = match.group(4)
                    if match_nick.lower() == nick.lower():
                        time_now = match.group(1)
                        type_chat = match.group(2)
                        prefixs = match.group(3)
                        message = match.group(5)
                        if type_chat == None:
                            type_chat = "Чат не определён"
                            
                        comparison["time"] = time_now
                        comparison["nickname"] = match_nick
                        comparison["message"] = message
                        comparison["prefixs"] = prefixs
                        comparison["type_chat"] = type_chat
                        
                        #print(f"{time_now} {type_chat} {prefixs}{Fore.RED}{match_nick}{Fore.WHITE}: {Fore.LIGHTYELLOW_EX}{message}\n")
                        print(pattern_general_chat.substitute(**comparison) + "\n")
                        

    elif mode_work == 4:
        nicks = set()
        for string in all_str:
            match = re.search('^' + reg_time + reg_logs_info + reg_mods_info + reg_type_chat + reg_prefixs + reg_nickname + ': ' + reg_message, string)
            if match:
                match_nick = match.group(4)
                nicks.add(match_nick)
        for nick in nicks:
            print()
            print(Fore.RED + nick)
        print()
    elif mode_work == 5:
        print("Включён режим отладки")
        while True:
            eval(input())
