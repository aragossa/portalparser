import json
import os
import time

import telebot

from dbconnector import Dbconnetor


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


def get_users ():
    dbconnector = Dbconnetor()
    query_result = dbconnector.execute_select_many_query("""
            SELECT user_id FROM oddsportalparser.ref_keys WHERE status = 'act'
        """)
    bot_users = []
    for row in query_result:
        bot_users.append(row[0])
    return bot_users


def get_state():
    pass

def change_state():
    pass




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



def update_prods (bot):
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