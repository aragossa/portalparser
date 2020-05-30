from bs4 import BeautifulSoup as Soup
import json
import datetime
import time
import uuid

# madrushspb
from selenium.common.exceptions import TimeoutException


def write_results(match_parse_results):
    print('start writing')
    filename = ('integration/{}.json'.format(uuid.uuid4()))
    print(filename)
    with open(filename, 'w') as fl:
        jsonObject = json.dumps(match_parse_results)
        print('# writing', jsonObject)
        fl.write(jsonObject)
        fl.write("\n")
    print('ok')


def write_results_to_db(match_parse_results):
    print('start writing')
    filename = ('dbintegration/{}.json'.format(uuid.uuid4()))
    print(filename)
    with open(filename, 'w') as fl:
        jsonObject = json.dumps(match_parse_results)
        print('# writing', jsonObject)
        fl.write(jsonObject)
        fl.write("\n")
    print('ok')


def convert_datetime(data):
    print(data)
    if 'Tomorr.' in data:
        dt = datetime.date.today() + datetime.timedelta(days=1)
        match_date = dt.strftime("%d/%m")
        match_time = data.replace('Tomorr.', '')
        return ('{0} - {1}'.format(match_date, match_time))

    elif 'Today' in data:
        dt = datetime.date.today()
        match_date = dt.strftime("%d/%m")
        match_time = data.replace('Today', '')
        return ('{0} - {1}'.format(match_date, match_time))

    else:
        match_time = data[5:]
        match_date = data[:5]
        # match_date = datetime.datetime.strptime(match_date, '%d/%m')
        # match_date = match_date.strftime("%d/%m")
        return ('{0} - {1}'.format(match_date, match_time))


# def save_results(odds):
#     query = ("""INSERT INTO parsedbet (user, sport_type, country, league, match_time, match_name, match_url, odd_1, odd_X, odd_2, pick)
#     VALUES ("{}","{}","{}","{}","{}","{}", "{}", "{}","{}", "{}",{})""".format(user, sport_type, country, league, match_time, match_name, match_url_o, odd_1, 'NONE', odd_2, pick))
#     pass


def prof_pars(driver, params, user, url):
    key_words = params.split(';')
    try:
        data = driver.page_source
    except TimeoutException:
        with open('errors.log', 'a', encoding='utf-8') as logfile:
            logfile.write(
                '---------\nTimeoutException\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), params, user, url))
        return None
    soup = Soup(data, "lxml")
    odd_res = {}
    feeds = soup.select('table#prediction-table-1 > tbody')
    for feed in feeds:
        tbl = feed.select('tr')
        odd_res = {}
        i = 0
        for elem in tbl:

            row_type = (i % 4)

            if row_type == 0:
                cell_vals = elem.select('th > a')
                print(cell_vals, cell_vals)
                try:

                    sport_type = cell_vals[0].text.strip().replace('\n', ' ')
                    country = cell_vals[1].text.strip().replace('\n', ' ')
                    league = cell_vals[2].text.strip().replace('\n', ' ')
                    odds = {
                        'user': user,
                        'sport_type': sport_type,
                        'country': country,
                        'league': league
                    }
                except IndexError:
                    with open('errors.log', 'a', encoding='utf-8') as logfile:
                        logfile.write(
                            '---------\IndexError\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), params, user, url))

                    continue
            elif row_type == 1:
                cell_vals = elem.select('td')
                if len(cell_vals) == 5:
                    try:
                        match_time = convert_datetime(cell_vals[0].text).replace('\n', ' ')
                    except ValueError:
                        with open('errors.log', 'a', encoding='utf-8') as logfile:
                            logfile.write(
                                '+++++++++\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), params, user, url))
                        time.sleep(3)
                        return data
                    match_name = cell_vals[1].text.strip().replace('\n', ' ')
                    try:
                        match_url = ('https://www.oddsportal.com{0}'.format(cell_vals[1].select_one('a').attrs['href']))
                    except AttributeError:
                        continue
                    odd_1 = cell_vals[2].text.strip()
                    odd_X = cell_vals[3].text.strip()
                    odd_2 = cell_vals[4].text.strip()
                    match_header = (match_name)
                    odds.update({
                        'match_time': match_time,
                        'match_name': match_name,
                        'match_url': match_url,
                        'odd_1': odd_1,
                        'odd_X': odd_X,
                        'odd_2': odd_2,
                    })
                elif len(cell_vals) == 4:
                    match_time = convert_datetime(cell_vals[0].text)
                    match_name = cell_vals[1].text.strip().replace('\n', ' ')
                    match_url = ('https://www.oddsportal.com{0}'.format(cell_vals[1].select_one('a').attrs['href']))
                    odd_1 = cell_vals[2].text.strip()
                    odd_2 = cell_vals[3].text.strip()
                    match_header = (match_name)
                    odds.update({
                        'match_time': match_time,
                        'match_name': match_name,
                        'match_url': match_url,
                        'odd_1': odd_1,
                        'odd_2': odd_2,
                    })


            elif row_type == 2:
                cell_vals = elem.select('td')
                counter = 0
                for cell in cell_vals:
                    try:
                        if cell.attrs['class'] == ['center', 'selected']:
                            pick = counter
                    except KeyError:
                        counter += 1
                odds.update({'pick': pick})
            elif row_type == 3:
                try:
                    odd_res.update({match_header: odds
                                    })
                    print ('oddsoddsoddsoddsodds')
                    #save_results (odds)
                    print ('oddsoddsoddsoddsodds')
                except UnboundLocalError:
                    i += 1
                    continue
            i += 1
    print('key_words', key_words)
    print('found', odd_res)
    print(url)
    if len(odd_res) > 0:
        if len(key_words) > 0:
            print('check keywords')
            for head, values in odd_res.copy().items():
                print(head)
                kw_count = 0
                for value in values.values():
                    print(key_words)
                    print(value)
                    print(value in key_words)
                    for key_word in key_words:
                        if key_word in str(value):
                            kw_count += 1
                if kw_count == 0:
                    print('no keyword found')
                    odd_res.pop(head)

            write_results(odd_res)
            write_results_to_db(odd_res)
        else:
            print('write all')
            write_results(odd_res)
            write_results_to_db(odd_res)
    else:
        print('nothing to write')
