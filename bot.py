# -*- coding: utf-8 -*-
import uuid

import psycopg2
import telebot
from telebot import types
from telebot import apihelper
import os
import threading
import schedule
import time
import json
from dbconnector import Dbconnetor
from update_prods import update_prods, get_users, read_intervals

token = '1265626051:AAHe9U4w-JwbjroAjUyydqGLhmF3sEUVonU'
#proxy = 'https://JLe3r1:UcW9VQ@196.18.3.112:8000'
proxy = '77.83.185.165:8000'
apihelper.proxy = {'https': proxy}
states = {}
states_user = {}

bot = telebot.TeleBot(token)

#https://t.me/Madbetbot?start=rus-tg-fpr






@bot.message_handler(commands=['start'])
def start_handler(m):
    dbconnector = Dbconnetor()
    ref_key = m.text.replace('/start ', '')
    if ref_key == '/start':
        bot.send_message (m.from_user.id, 'Не указан реферальный ключ')
    else:
        check = dbconnector.execute_select_query ("""SELECT ref_id from oddsportalparser.ref_keys WHERE ref_id = '{}' AND status = 'new'""".format(ref_key))
        if check:
            btn1 = types.KeyboardButton('Пользователи')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(btn1)
            try:
                dbconnector.execute_insert_query("""UPDATE oddsportalparser.ref_keys SET status = 'act', user_id = '{}'  WHERE ref_id = '{}'""".format(m.from_user.id, ref_key))
            except psycopg2.errors.UniqueViolation:
                bot.send_message (m.from_user.id, 'Вы уже зарегистрированы', reply_markup=keyboard)

            bot.send_message (m.from_user.id, 'Приветствую', reply_markup=keyboard)
        else:
            bot.send_message (m.from_user.id, 'Некорректный реферальный ключ')



@bot.message_handler(commands=['adddkkeeyyyc84c01eba1f44d386732825b0f259efyyyeekkddda'])
def add_key(m):
    dbconnector = Dbconnetor()
    new_key = uuid.uuid4()
    dbconnector.execute_insert_query("""INSERT INTO oddsportalparser.ref_keys (ref_id, status) VALUES ('{}', 'new')""".format(new_key))
    bot.send_message(m.from_user.id, 'Новый ключ:\n{}'.format(new_key))




@bot.message_handler(content_types= 'text' )
def start_handler(m):
    users = get_users()


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
        if (str(m.from_user.id) in users and m.text == 'Пользователи'):
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






def check_pending(bot):
    while True:
        schedule.run_pending()
        update_prods (bot)
        time.sleep(1)



th = threading.Thread(target=check_pending, args=(bot,))
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
