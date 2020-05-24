import pymysql
import os
import time
import json

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

def listener():
    con = pymysql.connect('31.31.198.110', 'u0862207_sherloc', 
     'admin!!!', 'u0862207_sherlock')
    for file in os.listdir ('dbintegration'):
        time.sleep (1)
        print (file)
        matches = dict(read_json ('dbintegration/{}'.format(file)))
        os.remove('dbintegration/{}'.format(file))
        for key, val in matches.items():
            send_msg = ''
            user = val.get('user')
            headers = key
            check_headers = ('{0}@{1}'.format(headers, user))


            with open('db_sent.txt', 'r') as send_f:
                sent_preds = send_f.readlines()
                
            check_preds = [pred.replace('\n', '') for pred in sent_preds]

            if check_headers in check_preds:
                print (check_headers, 'already send')
            elif headers == 'error':
                pass

            else:
                sport_type = val.get('sport_type')
                country = val.get('country')
                league = val.get('league')
                user = val.get('user')
                user_stat_url = 'https://www.oddsportal.com/profile/{}/statistics/'.format(user)
                print (len(val))
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

                    query = ("""INSERT INTO parsedbet (user, sport_type, country, league, match_time, match_name, match_url, odd_1, odd_X, odd_2, pick)
                    
    VALUES ("{}","{}","{}","{}","{}","{}", "{}", "{}","{}", "{}",{})""".format(user, sport_type, country, league, match_time, match_name, match_url_o, odd_1, 'NONE', odd_2, pick))
                    print (query)
                    with con:
                        cur = con.cursor()
                        cur.execute (query)
                    with open('db_sent.txt', 'a') as send_f:
                        send_f.write(check_headers)
                        send_f.write('\n')
                    time.sleep(1)
                
                
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
                    query = ("""INSERT INTO parsedbet (user, sport_type, country, league, match_time, match_name, match_url, odd_1, odd_X, odd_2, pick)
    VALUES ("{}","{}","{}","{}","{}","{}", "{}", "{}","{}", "{}",{})""".format(user, sport_type, country, league, match_time, match_name, match_url_o, odd_1, odd_X, odd_2, pick))
                    print (query)
                    with con:
                        cur = con.cursor()
                        cur.execute (query)
                    with open('db_sent.txt', 'a') as send_f:
                        send_f.write(check_headers)
                        send_f.write('\n')
                    time.sleep(1)
                    



if __name__ == '__main__':
    while True:
        listener()
        time.sleep(10)
