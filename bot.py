# -*- coding: utf-8 -*-

import telebot
from telebot import types
from telebot import apihelper
import os
import threading
import schedule
import time
import json
import traceback

token = '963152556:AAH9uhDHHmY4vdzC8R_EAg6uZKUONGVIjQI'
proxy = 'https://JLe3r1:UcW9VQ@196.18.3.112:8000'
#apihelper.proxy = {'https': proxy}
states = {}
states_user = {}

bot = telebot.TeleBot(token)



def read_json (filename):
    with open(filename, 'r') as log_file:
        read_products = log_file.readlines()
    #with open(filename, 'w') as log_file:
    #    log_file.write('')
    jsonObj = {}
    for elem in read_products:
        curr_obj = json.loads(elem)
        jsonObj.update(curr_obj)
    return jsonObj



def read_intervals():
    with open('cfgs.json', 'r') as log_file:
        read_products = log_file.readlines()
    jsonObj = {}
    for elem in read_products:
        curr_obj = json.loads(elem)
        jsonObj.update(curr_obj)
    return jsonObj

def check_intevals (cfgs, uid):

    response = ''
    if cfgs.get('x') == None:
        response += '-x'
    if cfgs.get('kb_min') == None:
        response += '-min'
    if cfgs.get('kb_max') == None:
        response += '-max'
    if cfgs.get('bk1') == None:
        response += '-bk1'
    if cfgs.get('bk2') == None:
        response += '-bk2'
    return response


def update_prods ():

    admins = []
    with open('admins.cfg', 'r') as users_file:
        for admin in users_file.readlines():
            if admin != '\n' or admin != '':
                admins.append (admin.rstrip())
    with open('active_usr', 'r') as state:
        bot_users = state.readlines()

    with open('active_groups', 'r') as state:
        bot_groups = state.readlines()
    for file in os.listdir ('integration'):
        time.sleep (1)
        matches = dict(read_json ('integration/{}'.format(file)))
        os.remove('integration/{}'.format(file))

        for key, val in matches.items():
            send_msg = ''
            user = val.get('user')
            headers = key
            check_headers = ('{0}@{1}'.format(headers, user))


            with open('sent.txt', 'r') as send_f:
                sent_preds = send_f.readlines()
            check_preds = [pred.replace('\n', '') for pred in sent_preds]

            if check_headers in check_preds:
                print (check_headers, 'already send')
                continue
            elif headers == 'error':
                pass
                #send_msg = (val)
                #
                #for admin in admins:
                #    try:
                #        bot.send_message (admin, send_msg)
                #    except telebot.apihelper.ApiException:
                #        admins.remove (admin)
                #        with open('admins.cfg', 'w') as admin_file:
                #            for admin in admins:
                #                admin_file.write(admin)




            else:
                sport_type = val.get('sport_type')
                country = val.get('country')
                league = val.get('league')
                user = val.get('user')
                cfgs = read_intervals()
                params = cfgs.get(user)
                user_stat_url = 'https://www.oddsportal.com/profile/{}/statistics/'.format(user)
                send_msg = ("""\nby {0} (key words: {1})\n""".format(user, params))
                if len(val) == 10:
                    sport_type = val.get('sport_type')
                    country = val.get('country')
                    league = val.get('league')
                    match_time = val.get('match_time')
                    match_name = val.get('match_name')
                    match_url_b = val.get('match_url').replace('oddsportal.com', 'betexplorer.com')
                    match_url_o = val.get('match_url')
                    odd_1 = val.get('odd_1')
                    odd_2 = val.get('odd_2')
                    pick = val.get('pick')

                    if pick == 0:
                        odd_1 = (odd_1 + ' (PICK)')
                    elif pick == 1:
                        odd_2 = (odd_2 + ' (PICK)')
                    send_msg += ("""{0} ({2})
    {1}
    {4} ({3})
    odds: {5} - {6})""".format(match_name, match_time, sport_type, country, league, odd_1, odd_2, match_url_o, user, params, match_url_b, user_stat_url))
                elif len(val) == 11:
                    match_time = val.get('match_time')
                    match_name = val.get('match_name')
                    match_url_b = val.get('match_url').replace('oddsportal.com', 'betexplorer.com')
                    match_url_o = val.get('match_url')
                    odd_1 = val.get('odd_1')
                    odd_X = val.get('odd_X')
                    odd_2 = val.get('odd_2')
                    pick = val.get('pick')
                    if pick == 0:
                        odd_1 = (odd_1 + ' (PICK)')
                    elif pick == 1:
                        odd_X = (odd_X + ' (PICK)')
                    elif pick == 2:
                        odd_2 = (odd_2 + ' (PICK)')
                    send_msg += ("""{0} ({2})
    {1}
    {4} ({3})
    odds: {5} - {6} - {7}""".format(match_name, match_time, sport_type, country, league, odd_1, odd_X, odd_2, match_url_o, user, params, match_url_b, user_stat_url))
                elif len(val) == 7:

                    wc_winner = val.get('wc_winner')
                    odd_wc = val.get('odd_wc')
                    send_msg += ("""{0} ({1})
    {2}
    odds: {3}""".format(league, sport_type, wc_winner, odd_wc, user,params))



                #else:
                #    send_msg = str(val)

                if len(val) == 10:
                    send_msg += ("""\n{0}\n{1}\n""".format(match_url_b, match_url_o))

                elif len(val) == 11:
                    send_msg += ("""\n{0}\n{1}\n""".format(match_url_b, match_url_o))

                if user == 'madrush':

                    for group in bot_groups:
                        print ('group', group)
                        try:
                            bot.send_message (group, send_msg)
                        except telebot.apihelper.ApiException as e:
                        	print (e)
                            #with open ('group_errors', 'a') as group_error_file:
                            #    group_error_file.write('\n')
                            #    group_error_file.write (group)


                print (send_msg)
                #if len(val) == 10:
                #    send_msg += ("""\nby {0} (key words: {1})\n""".format(user, params))

                #elif len(val) == 11:
                #    send_msg += ("""\nby {0} (key words: {1})\n""".format(user, params ))

                #elif len(val) == 7:
                #    send_msg += ("""\nby {0} (key words: {1})\n""".format(user, params))

                if len(val) != 7:
                    send_msg += ("""{0}""".format(user_stat_url))

                for bot_user in bot_users:
                    try:
                        bot.send_message (bot_user, send_msg)
                    except telebot.apihelper.ApiException as e:
                        with open ('user_errors', 'a') as user_error_file:

                            user_error_file.write (bot_user)
                            user_error_file.write('\n')

                with open('sent.txt', 'a') as send_f:
                    send_f.write(check_headers)
                    send_f.write('\n')

@bot.message_handler(commands=['start'])
def start_handler(m):
    admins = []
    with open('admins.cfg', 'r') as users_file:
        for admin in users_file.readlines():
            if admin != '\n' or admin != '':
                admins.append (admin.rstrip())
    if str(m.from_user.id) in admins:
        btn1 = types.KeyboardButton('Пользователи')


        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(btn1)

        bot.send_message (m.from_user.id, 'Приветствую', reply_markup=keyboard)
    else:
        bot.send_message (m.from_user.id, 'Вы не авторизованы')

@bot.message_handler(commands=['getgroupid'])
def on_info(m):
    bot.reply_to(m, m.chat.id)

@bot.message_handler(commands=['addgroupreciver'])
def addgroupreciver(m):
    admins = []
    with open('admins.cfg', 'r') as users_file:
        for admin in users_file.readlines():
            if admin != '\n' or admin != '':
                admins.append (admin.rstrip())
    print (m.chat.id)
    print (admins)
    if str(m.chat.id) in admins:
        bot.send_message (m.from_user.id, 'Группа добавлена')
        with open('active_groups', 'a') as admin_file:
            admin_file.write('\n')
            admin_file.write(str(m.text.split()[1]))
    else:
        bot.send_message (m.from_user.id, 'В доступе отказано')



@bot.message_handler(commands=['startadmining'])
def add_admin(m):
    gen_id = ('HJlIkuv564#$$#%nm4564567862r9nasmds')
    print (m.text)
    if (m.text.split()[1]) == gen_id:
        bot.send_message (m.from_user.id, 'Вы авторизованы')
        with open('admins.cfg', 'a') as admin_file:
            admin_file.write(str(m.from_user.id))
            admin_file.write('\n')
        with open('active_usr', 'a') as admin_file:
            admin_file.write(str(m.from_user.id))
            admin_file.write('\n')
    else:
        bot.send_message (m.from_user.id, 'Неизвестная команда')


@bot.message_handler(commands=['joinnotification'])
def add_user(m):
    try:
        gen_id = m.text.split()[1]
        if gen_id == '786267edhGGDggfhs55yr9nasmds':
            bot.send_message (m.from_user.id, 'Вы авторизованы')
            with open('active_usr', 'a') as admin_file:
                admin_file.write(str(m.from_user.id))
                admin_file.write('\n')
        else:
            bot.send_message (m.from_user.id, 'Код авторизации недействительный')
    except Exception as e:
        print (e)
        print (m.text)
        print (m.chat.id)
        bot.send_message (m.from_user.id, 'Код авторизации недействительный')


@bot.message_handler(content_types= 'text' )
def start_handler(m):
    admins = []
    with open('admins.cfg', 'r') as users_file:
        for admin in users_file.readlines():
            if admin != '\n' or admin != '':
                admins.append (admin.rstrip())
    print ('state', states.get(m.from_user.id))


    if (states.get(m.from_user.id) == 'add_user'):
        input_data = m.text
        print ('adding user', input_data)

        cfgs = read_intervals()
        cfgs.update ({input_data: '',
                      })
        with open('cfgs.json', 'w') as fl:
            jsonObject = json.dumps(cfgs)
            fl.write(jsonObject)
        bot.send_message (m.chat.id, 'Пользователь добавлен в список, если нужно добавить ключевые слова для фильтра матчей выберите Пользователи -> Показать/удалить пользователей -> Добавить ключевые слова')
        states[m.chat.id] = ''



    elif (states.get(m.from_user.id) == 'kw'):
        input_data = m.text
        enter_val = states_user.get(m.from_user.id)
        cfgs = read_intervals()
        cfgs.update ({enter_val: input_data,
                      })
        with open('cfgs.json', 'w') as fl:
            jsonObject = json.dumps(cfgs)
            fl.write(jsonObject)
        bot.send_message (m.from_user.id, 'Данные обновлены')
        states[m.from_user.id] = ''
        states_user[m.from_user.id] = ''


    else:
        if (str(m.from_user.id) in admins and m.text == 'Пользователи'):
            keyboard = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton (text= 'Показать/удалить пользователей', callback_data='list_user')
            btn2 = types.InlineKeyboardButton (text= 'Добавить пользователя', callback_data='add_user')

            keyboard.add (btn1, btn2)
            bot.send_message(m.chat.id, text=('Выберите действие'), reply_markup=keyboard)

        else:
            bot.send_message (m.from_user.id, 'Команда не распознана', parse_mode="HTML")




@bot.callback_query_handler(func=lambda call:  (call.data == 'add_user'))
def add_user  (call):
    states[call.message.chat.id] = 'add_user'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('Введите имя пользователя'))




@bot.callback_query_handler(func=lambda call:  (call.data == 'list_user'))
def list_user  (call):
    portal_users = read_intervals()

    if portal_users == None:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('Пользователи не заданы'))
    else:

        msg_text = 'Пользователи:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text)

        for user, params in portal_users.items():
            #states_user[call.message.chat.id] = user
            keyboard = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton (text= 'Удалить', callback_data='del{}'.format(user))
            btn2 = types.InlineKeyboardButton (text= 'Ввести ключевые слова', callback_data='kw{}'.format(user))
            keyboard.add (btn1, btn2)
            if params == '':
                send_params = ('Ключевые слова не заданы')
            else:
                send_params = params

            msg_text = ('{0}: {1}'.format (user, send_params))
            bot.send_message(chat_id=call.message.chat.id, text=msg_text, reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call:  (call.data[:3] == 'del'))
def del_user  (call):
    del_val = call.data[3:]
    cfgs = read_intervals()
    cfgs.pop (del_val)

    with open('cfgs.json', 'w') as fl:
        jsonObject = json.dumps(cfgs)
        fl.write(jsonObject)
    msg_text = ('Пользователь портала {0} удален'.format (del_val))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text)
    states_user[call.message.chat.id] = ''

@bot.callback_query_handler(func=lambda call:  (call.data[:2] == 'kw'))
def enter_kw  (call):
    states[call.message.chat.id] = 'kw'
    states_user[call.message.chat.id] = call.data[2:]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('Укажите ключевые слова через разделитель ";"'))






def check_pending():
    while True:
        #print ('Running pending')
        #print (threading.current_thread())
        schedule.run_pending()
        update_prods ()
        time.sleep(1)



th = threading.Thread(target=check_pending, args=())
print ('start pending thread')
th.start()


while True:
    try:
        print ('Listernig...')
        print (threading.current_thread())
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(5)
