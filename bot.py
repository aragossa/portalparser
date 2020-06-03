# -*- coding: utf-8 -*-
import uuid

import telebot
from telebot import types
from telebot import apihelper
import threading
import schedule
import time
from dbconnector import Dbconnetor
from mainlogger import get_logger
from update_prods import update_prods, get_users


token = '1265626051:AAHe9U4w-JwbjroAjUyydqGLhmF3sEUVonU'
# proxy = 'https://JLe3r1:UcW9VQ@196.18.3.112:8000'
proxy = '77.83.185.165:8000'
apihelper.proxy = {'https': proxy}
states = {}
states_user = {}

bot = telebot.TeleBot(token)
parser_logger = get_logger("bot")


# https://t.me/Madbetbot?start=rus-tg-fpr


@bot.message_handler(commands=['start'])
def start_handler(m):
    dbconnector = Dbconnetor()
    ref_key = m.text.replace('/start ', '')
    if ref_key == '/start':
        bot.send_message(m.from_user.id, 'Не указан реферальный ключ')
    else:
        check = dbconnector.execute_select_query(
            """SELECT ref_id from oddsportalparser.ref_keys WHERE ref_id = '{}' AND status = 'new'""".format(ref_key))
        if check:
            btn1 = types.KeyboardButton('Manage portal users')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(btn1)
            try:
                dbconnector.execute_insert_query(
                    """UPDATE oddsportalparser.ref_keys SET status = 'act', user_id = '{}'  WHERE ref_id = '{}'""".format(
                        m.from_user.id, ref_key))
            except:
                bot.send_message(m.from_user.id, 'You are allready in', reply_markup=keyboard)

            bot.send_message(m.from_user.id, 'Welocome', reply_markup=keyboard)
        else:
            bot.send_message(m.from_user.id, 'Wrong referal key')


@bot.message_handler(commands=['adddkkeeyyyc84c01eba1f44d386732825b0f259efyyyeekkddda'])
def add_key(m):
    if m.chat.id in [746474879, 556047985]:
        dbconnector = Dbconnetor()
        new_key = uuid.uuid4()
        dbconnector.execute_insert_query(
            """INSERT INTO oddsportalparser.ref_keys (ref_id, status) VALUES ('{}', 'new')""".format(new_key))
        bot.send_message(m.from_user.id, 'Bot referal url:\nt.me/Madbetbot?start={}'.format(new_key))
    else:
        bot.send_message(m.from_user.id, 'Access denied')


@bot.message_handler(content_types='text')
def start_handler(m):
    users = get_users()

    if (str(m.from_user.id) in users and m.text == 'Manage portal users'):
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Show/remove portal users', callback_data='list_user')
        btn2 = types.InlineKeyboardButton(text='Add portal user', callback_data='add_user')

        keyboard.add(btn1, btn2)
        bot.send_message(m.chat.id, text=('Make A choice'), reply_markup=keyboard)


    elif (states.get(m.from_user.id) == 'add_user'):
        dbconnector = Dbconnetor()
        input_data = m.text
        parser_logger.info('adding user {}'.format(input_data))
        dbconnector.execute_insert_query("""INSERT INTO oddsportalparser.configs
        (bot_user_id, portal_user_name, source_type)
        VALUES('{}', '{}', '');
        """.format(m.chat.id, input_data))
        dbconnector.execute_insert_query("""UPDATE oddsportalparser.ref_keys
        SET input_value='{}'
        WHERE user_id='{}';
        """.format(input_data, m.chat.id))
        bot.send_message(m.chat.id, 'Done')
        states[m.chat.id] = ''



    elif (states.get(m.from_user.id) == 'kw'):
        dbconnector = Dbconnetor()
        input_data = m.text
        portal_user_name = dbconnector.execute_select_query("""
        SELECT input_value
        FROM oddsportalparser.ref_keys
        WHERE user_id = '{}';
        """.format(m.chat.id))

        dbconnector.execute_insert_query("""UPDATE oddsportalparser.configs
            SET source_type='{}'
            WHERE portal_user_name='{}' AND bot_user_id = '{}';
            """.format(input_data, portal_user_name[0], m.chat.id))

        bot.send_message(m.from_user.id, 'Done')
        states[m.from_user.id] = ''
        states_user[m.from_user.id] = ''


    else:
        bot.send_message(m.from_user.id, 'Unexpected command', parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: (call.data == 'add_user'))
def add_user(call):
    states[call.message.chat.id] = 'add_user'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('Enter username'))


@bot.callback_query_handler(func=lambda call: (call.data == 'list_user'))
def list_user(call):
    # portal_users = read_intervals()
    dbconntector = Dbconnetor()
    portal_users = dbconntector.execute_select_many_query("""
        SELECT portal_user_name, source_type
        FROM oddsportalparser.configs
        WHERE bot_user_id = '{}';
        """.format(call.message.chat.id))

    if portal_users == None:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=('No active portal users'))
    else:
        msg_text = 'Your users:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text)
        for elem in portal_users:
            user = elem[0]
            params = elem[1]
            # states_user[call.message.chat.id] = user
            keyboard = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Delete', callback_data='del{}'.format(user))
            btn2 = types.InlineKeyboardButton(text='Enter keywords', callback_data='kw{}'.format(user))
            keyboard.add(btn1, btn2)
            if params == '':
                send_params = ('No keywords')
            else:
                send_params = params

            msg_text = ('{0}: {1}'.format(user, send_params))
            bot.send_message(chat_id=call.message.chat.id, text=msg_text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: (call.data[:3] == 'del'))
def del_user(call):
    dbconnector = Dbconnetor()
    del_val = call.data[3:]
    dbconnector.execute_insert_query(query="""
    DELETE FROM oddsportalparser.configs
    WHERE portal_user_name='{}' AND bot_user_id ='{}';
    """.format(del_val, call.message.chat.id))

    msg_text = ('Deleted user {0}'.format(del_val))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text)
    states_user[call.message.chat.id] = ''


@bot.callback_query_handler(func=lambda call: (call.data[:2] == 'kw'))
def enter_kw(call):
    states[call.message.chat.id] = 'kw'
    input_data = call.data[2:]
    dbconnector = Dbconnetor()
    dbconnector.execute_insert_query("""UPDATE oddsportalparser.ref_keys
        SET input_value='{}'
        WHERE user_id='{}';
        """.format(input_data, call.message.chat.id))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=('Enter keywords through the separator ";"'))


def check_pending(bot):
    while True:
        schedule.run_pending()
        update_prods(bot)
        time.sleep(1)


th = threading.Thread(target=check_pending, args=(bot,))
parser_logger.info('start pending thread')
th.start()

while True:
    try:
        parser_logger.info('Listernig...')
        bot.polling(none_stop=True)
    except Exception as e:
        parser_logger.exception(e)
        time.sleep(5)
