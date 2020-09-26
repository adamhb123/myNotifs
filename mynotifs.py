__author__ = "Adam Brewer"

from selenium import webdriver
import sqlite3, time, platform
import pynotifier, json
from threading import Thread

from pathlib import Path

"""db = sqlite3.connect('notifications.db')
db.execute('''CREATE TABLE IF NOT EXISTS notifications
             (notification text)''')"""


NOTIF_WAIT_TIME = 4
SITE_WAIT_TIME = 6
OPSYS = platform.system().lower()
ICONDIR = Path('./icons').absolute()
HOMEPAGE = "https://mycourses.rit.edu/d2l/home"

def load_cookies(wdriver: webdriver.Firefox=None,filename='lastsesh.cookies'):
    #   HAVE TO SAVE AND LOAD COOKIES ON SAME PAGE
    wdriver.get(HOMEPAGE)
    time.sleep(SITE_WAIT_TIME)
    cookies = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for cookie in lines:
            cookie = json.loads(cookie)
            cookies.append(cookie)
            if wdriver is not None:
                driver.add_cookie(cookie)
    return cookies

firefoxOptions = webdriver.FirefoxOptions()
#firefoxOptions.headless = True
driver = webdriver.Firefox(executable_path=
                           str(Path('./geckodriver.exe').absolute())
                           if 'windows' in OPSYS else str(Path('./geckodriver').absolute()),
                           options=firefoxOptions)
try:
    load_cookies(driver)
except Exception as e:
    print(e)
    driver.delete_all_cookies()


class CCNotification(pynotifier.Notification):
    ICON_LOGO = "icon"

    def __init__(self, title, description, duration=5, urgency=pynotifier.Notification.URGENCY_LOW):
        if "windows" in OPSYS:
            icon_path = f"{ICONDIR}/{self.ICON_LOGO}.ico"
        else:
            icon_path = f"{ICONDIR}/{self.ICON_LOGO}.png"
        super().__init__(title, description, duration=duration, urgency=urgency, icon_path=icon_path)


def grab_mc_notifs(driver: webdriver.Firefox):
    if not driver.current_url == HOMEPAGE:
        driver.get(HOMEPAGE)
        time.sleep(SITE_WAIT_TIME)
    elems = driver.find_elements_by_css_selector("d2l-navigation-button-notification-icon")
    notification_button = None
    for elem in elems:
        if 'notification' in elem.get_attribute('icon'):
            notification_button = elem
    if not notification_button:
        raise
    notification_button.click()
    #   Expand notification list
    time.sleep(SITE_WAIT_TIME)
    notifs = driver.find_element_by_xpath('//ul[@class="d2l-datalist vui-list"]')
    notifs = notifs.find_elements_by_xpath("./*")
    nlist = []
    for indiv_notif in notifs:
        try:
            nlist.append(indiv_notif.find_elements_by_xpath("./*")[0].get_attribute('title'))
        except:
            continue
    #   WOULD USE DB, CAN'T NOW NOT ENOUGH TIME
    #db.execute("INSERT INTO notifications VALUES (?)",n)
    with open('pseudodb.txt','r') as f:
        for line in f.readlines():
            found = False
            for n in nlist:
                print("%s in %s?" % (n,str(line)))
                if n.strip().lower().replace('\n','') == line.strip().lower().replace('\n',''):
                    found = True
                    break
            if not found:
                print("NOT FOUND")
                notify("New MyCourses Notification!", line)
        #   Update file with latest notifs
    with open('pseudodb.txt', 'w') as f:
        for n in nlist:
            f.write(f'{n}\n')

    # driver.find




def save_cookies(wdriver: webdriver.Firefox, filename='lastsesh.cookies', exit=False):
    #   Save cookies (hopefully login info) before exit
    #   HAVE TO LOAD AND SAVE COOKIES ON SAME PAGE
    wdriver.get("https://mycourses.rit.edu/d2l/home")
    time.sleep(SITE_WAIT_TIME)
    cookies = wdriver.get_cookies()
    with open(filename, 'w+') as f:
        for cookie in cookies:
            f.write(json.dumps(cookie)+'\n')

    if exit:
        wdriver.close()
    return cookies


def notifops(wdriver):
    """
    Notification looping thread

    :return: None
    """
    #   User is (hopefully) logged in
    notify(title="Logged in to MyCourses!", description="Successfully logged into MyCourses and booted up!")
    while True:
        try:
            grab_mc_notifs(driver)
        except Exception as e:
            print(f"Lol: {e}")
    # while True:
    # if notif_in_db(grab_mc_notifs)
    #    time.sleep(60)


def notify(title, description, duration=NOTIF_WAIT_TIME, urgency=CCNotification.URGENCY_NORMAL):
    try:
        CCNotification(
            title,
            description,
            duration=duration,
            urgency=urgency
        ).send()
    except AttributeError:
        print("Failed, probably win10toast. Don't care. Oops.")

def copy_cookies(fromd:webdriver.Firefox,tod:webdriver.Firefox,clear=False):
    if clear: tod.delete_all_cookies()
    for cookie in fromd.get_cookies():
        tod.add_cookie(cookie)

def login():
    #   Create temporary driver to get user to login,
    #   save cookies to import to main driver in future use,
    #   return cookies to use in driver for current session
    temp_driver = webdriver.Firefox()
    temp_driver.get(HOMEPAGE)
    time.sleep(SITE_WAIT_TIME)
    try:
        button = temp_driver.find_element_by_id("link1")
        button.click()
        print("BUTTON CLICKED, GO LOGIN")
    except:
        print("User probably hit login button already I guess idk who cares")
    notify("Please Login!",
           "Please login to MyCourses in the popup browser and select 'Remember me for 7 days!",
           urgency=CCNotification.URGENCY_CRITICAL)
    time.sleep(SITE_WAIT_TIME)
    while "shibboleth.main.ad.rit.edu" in temp_driver.current_url:
        time.sleep(SITE_WAIT_TIME)
    cookies = save_cookies(temp_driver, exit=True)
    return cookies

def main():
    driver.get(HOMEPAGE)
    time.sleep(SITE_WAIT_TIME)
    button = driver.find_element_by_id("link1")
    if button:
        #   User is (hopefully) not logged in
        #   Open a popup window and have the user login
        login()
        load_cookies(wdriver=driver)

    #   User is (hopefully) logged in, start notifop loop
    driver.get(HOMEPAGE)
    notifops(driver)

def quicker_test():
    driver.get(HOMEPAGE)
    input("LOGIN")
    notifops(driver)

if __name__ == "__main__":
    main()
