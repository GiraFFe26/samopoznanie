from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
import chromedriver_binary
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


def collect_data(url):
    ua = UserAgent()
    pause = 0.5
    delay = 3
    SCROLL_PAUSE_TIME = 1.5
    phones, works, names = [], [], []
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument(f'user-agent={ua.random}')
    # chromeOptions.add_argument("--headless")
    chromeOptions.add_argument('window-size=1920x1080')
    chromeOptions.add_argument('--disable-dev-shm-usage')
    chromeOptions.add_argument('--ignore-certificate-errors')
    chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
    chromeOptions.add_argument('--log-level=1')
    chromeOptions.add_argument("--disable-setuid-sandbox")
    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--disable-gpu")
    chromeOptions.add_argument("disable-infobars")
    chromeOptions.add_argument("--remote-debugging-port=9224")
    driver = webdriver.Chrome(options=chromeOptions)
    driver.get(url)
    time.sleep(pause)
    while True:
        try:
            driver.find_element(By.CLASS_NAME, 'objects_read_more_link').click()
            time.sleep(SCROLL_PAUSE_TIME)
        except (NoSuchElementException, ElementClickInterceptedException):
            break
    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml')
    trainers = soup.find_all('div', class_='artWrap org_list')
    print(len(trainers))
    for trainer in trainers:
        tr = trainer.find('div', class_='artHeader').find('a')
        name = tr.text
        url = 'https://samopoznanie.ru' + tr.get('href')
        driver.get(url)
        try:
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CLASS_NAME, 'border_bot')))
        except TimeoutException:
            time.sleep(delay)
        try:
            but = driver.find_element(By.CLASS_NAME, 'border_bot')
        except NoSuchElementException:
            continue
        if 'телефон' in but.text:
            but.click()
        else:
            continue
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'phone-box')))
        except TimeoutException:
            time.sleep(delay)
        src = driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        phone = soup.find('div', class_='phone_wrap').text
        names.append(name)
        phones.append(phone)
    df = pd.DataFrame({'Организация': names,
                       'Телефон': phones})
    df.to_excel('orgs.xlsx', index=False)


def main():
    collect_data('https://samopoznanie.ru/msk/organizers/')


if __name__ == "__main__":
    main()
