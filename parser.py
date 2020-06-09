from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from dbconnector import Dbconnetor
from prof_pars import prof_pars
import time
import datetime
import random
import traceback

fin_cfg = {'ip':'77.83.185.165:8000',
           'user':'aragesserf',
           'pass':'iafpfi'}

ger_cfg = {'ip':'77.83.185.165:8000',
           'user':'aragesserg',
           'pass':'iafpfi'}

main_cfg = [fin_cfg, ger_cfg]



def login(driver, username, pwd):
    print ('login')
    driver.find_element_by_class_name ('inline-btn-2').click()
    element = driver.find_element_by_id("login-username1")
    element.send_keys(username)
    element = driver.find_element_by_id("login-password1")
    element.send_keys(pwd)
    btns = driver.find_elements_by_name("login-submit")
    btns[1].click()

def pagination(driver, user):
    #start
    data = driver.page_source
    soup = Soup (data, "lxml")
    pagination_div = soup.find('div', {'id':'pagination'})
    if pagination_div != None:
        pages_urls = []
        check_url = ('https://www.oddsportal.com/profile/{}/my-predictions/next/page/'.format(user))
        for a_tag in pagination_div.find_all('a', href = True):
            page_url = ('https://www.oddsportal.com{0}'.format(a_tag.attrs['href']))
            if (check_url in page_url) and (page_url not in pages_urls):
                pages_urls.append(page_url)
        return pages_urls
    else:
        return None


def get_portal_users():
    dbconnetor = Dbconnetor()
    query_result = dbconnetor.execute_select_many_query("""
            SELECT portal_user_name, source_type
            FROM oddsportalparser.configs;
            """)
    portal_users = []
    for row in query_result:
        portal_users.append(str(row[0]))
    return portal_users




def main_func(driver, config):

    dbconnetor = Dbconnetor()
    start = ("https://www.oddsportal.com/login")
    driver.get(start)
    login(driver, config.get('user'), config.get('pass'))
    set_timezone = 'https://www.oddsportal.com/full_time_zone/54/'
    driver.get(set_timezone)
    print ('time zone - 54')

    while True:
        start_time = time.time()
        portal_users = get_portal_users()
        for user in portal_users:
            url = 'https://www.oddsportal.com/profile/{}/my-predictions/next/'.format(user)
            try:
                driver.get(url)
            except TimeoutException:
                with open('errors.log', 'a', encoding='utf-8') as logfile:
                    logfile.write('---------\nTimeoutException\n{}\n{}\n{}\n'.format(datetime.datetime.now(), user, curr_url))

                continue
            pages_urls = pagination(driver, user)
            prof_pars (driver, user, url)
            if pages_urls != None:
                for curr_url in pages_urls:
                    driver.get(curr_url)
                    try:
                        prof_pars (driver, user, curr_url)
                        time.sleep(3)
                    except Exception as e:
                        with open('errors.log', 'a', encoding='utf-8') as logfile:
                            logfile.write('---------\n{}\n{}\n{}\n{}\n'.format(datetime.datetime.now(), user, curr_url, e))
                            logfile.write(traceback.format_exc())
                        time.sleep(3)


            time.sleep(3)
        print ('whole time', time.time() - start_time)
        time.sleep(300)



def main ():
    while True:

        print ('starting')

        select = random.randint(0, 1)
        config = main_cfg[select]
        print (config)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=http://%s' % config.get('ip'))
        chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.
        driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)#,
        service_args=['--verbose', '--log-path=/tmp/chromedriver.log']
        try:
            main_func(driver, config)
        except Exception as e:
            print (e)
            time.sleep(10)
            driver.close()
            with open('errors.log', 'a', encoding='utf-8') as logfile:
                logfile.write('---------\n{}\n{}'.format(datetime.datetime.now(), e))
            print ('sleeping')
            time.sleep(20)



if __name__ == '__main__':
    main()