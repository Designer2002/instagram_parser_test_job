import argparse
import os
import platform
import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.ie.service import Service as IEService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager, EdgeChromiumDriverManager

def get_browser_path(browser):
    if browser.lower() == 'chrome':
        if platform.system() == 'Windows':
            paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe'
        ]
            return check_windows_path(paths)
        elif platform.system() == 'Darwin':  # macOS
            return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        else:  # Linux
            return '/usr/bin/google-chrome'
    elif browser.lower() == 'firefox':
        if platform.system() == 'Windows':
            paths = [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
            r'C:\Users\%USERNAME%\AppData\Local\Mozilla Firefox\firefox.exe'
        ]
            return check_windows_path(paths)
        elif platform.system() == 'Darwin':  # macOS
            return '/Applications/Firefox.app/Contents/MacOS/firefox'
        else:  # Linux
            return '/usr/bin/firefox'
    elif browser.lower() == 'edge':
        if platform.system() == 'Windows':
            paths = [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
            r'C:\Users\%USERNAME%\AppData\Local\Microsoft\Edge\Application\msedge.exe'
        ]
            return check_windows_path(paths)
        elif platform.system() == 'Darwin':  # macOS
            return '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
        else:  # Linux
            return '/usr/bin/microsoft-edge'
    elif browser.lower() == 'ie':
        if platform.system() == 'Windows':
            paths = [
            r'C:\Program Files\Internet Explorer\iexplore.exe',
            r'C:\Program Files (x86)\Internet Explorer\iexplore.exe'
        ]
            return check_windows_path(paths)
    return None

def check_windows_path(paths):
    for path in paths:
        expanded_path = os.path.expandvars(path) 
        if os.path.exists(expanded_path):
            return expanded_path
    return None

def main(nickname, browser, custom_path):
    print("Запускаю поиск браузера для парсинга профиля. Это может занять время, но ничего не зависло, так надо, правда.")
    if custom_path:
        browser_path = custom_path
    else:
        browser_path = get_browser_path(browser)

    options = None
    if browser.lower() == 'chrome':
        options = webdriver.ChromeOptions()
        options.binary_location = browser_path
        options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-insecure-localhost')  
        options.add_argument('--ssl-protocol=tls1.2')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif browser.lower() == 'firefox':
        options = webdriver.FirefoxOptions()
        options.binary_location = browser_path
        options.add_argument('--headless') 
        options.set_preference('security.mixed_content.block_active_content', False)
        options.set_preference('security.mixed_content.block_active_content', False) 
        options.set_preference("security.tls.version.max", 3)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    elif browser.lower() == 'edge':
        options = webdriver.EdgeOptions()
        options.binary_location = browser_path
        options.add_argument('--headless')  
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-insecure-localhost')  
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)

    elif browser.lower() == 'ie':
        options = webdriver.IeOptions()
        options.binary_location = browser_path
        options.add_argument('--headless')  
        options.ignore_zoom_settings = True  
        options.ensure_clean_session = True  
        options.add_argument('--ignore-certificate-errors')  
        driver = webdriver.Ie(service=IEService(IEDriverManager().install()), options=options)

    else:
        print("Моя программа поддерживает только Chrome, Firefox, Edge и Internet Explorer. Установите, пожалуйста, что-то из этих браузеров себе, чтобы всё корректно работало.")
        return

    try:
        print("Браузер найден! Сейчас будет магия! Шутка, к сожалению - сейчас будет всё снова очень долго грузится, но Вы не закрывайте программу, она не зависла, просто думает. Могут печататься разные ошибки, но не стоит на них обращать внимания. Если случится какая-то действительно мешающая работать ошибка, то я уведомлю и совершу выход из программы.")
        driver.get('https://insta-save.net/instafinsta/')          
        print(f"Ищу посты профиля: {nickname}")

        # поле ввода
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='link']"))
        )
        input_field.clear()
        input_field.click()
        time.sleep(0.5)
        input_field.send_keys(nickname)
        time.sleep(0.5)

        # кнопка СКАЧАТЬ
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='downloadButton']"))
        )
        button.click()

        # ждем пока грузится
        info_div = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='d-flex justify-content-around text-center mt-3']"))
        )
        info_li = info_div.find_elements(By.XPATH, "//span[@class='d-block h5 mb-0']")

        # получили инфу и свалили в json
        posts = info_li[0].text
        followers = info_li[1].text
        info_json = json.dumps({
            "followers": followers,
            "posts": posts
        })
        

        # ждем пока появится кнопка POSTS
        posts_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='nav-link allbtn ' and contains(text(), 'POSTS')]"))
        )
        posts_button.click()

        # ждем пока загрузятся посты после нажатия
        posts_data_cols = WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='col-md-4 position-relative']"))
        )
        posts_info = []

        for col in posts_data_cols:
            # описание поста
            description = col.find_element(By.XPATH, ".//p[@class='text-sm']").text  

            # лайки и дата
            likes_and_date = col.find_elements(By.XPATH, ".//div[@class='stats text-sm']")
            likes = likes_and_date[0].find_element(By.XPATH, ".//small").text.strip() 
            date = likes_and_date[1].find_element(By.XPATH, ".//small").text.strip()  

            # количество комментариев
            comments = col.find_element(By.XPATH, ".//div[@class='stats text-sm text-center']").find_element(By.XPATH, ".//small").text.strip() 
            # словарь
            collected_info = {
                "Описание поста (caption)": description,
                "Лайки": likes,
                "Комментарии": comments,
                "Дата публикации": date
            }
            
            posts_info.append(collected_info)

        
        #запись в csv
        filename = "out.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=posts_info[0].keys())  
            writer.writeheader()  
            for row in posts_info:
                writer.writerow(row) 
        print("Сбор информации завершен успешно!")
        print("Эти данные функция вернет, но вот они Вам на всякий случай:\n", info_json)
        print("Общая информация возвращена в виде JSON, информация о постах представлена в виде CSV файла out.csv")
        return info_json
    except Exception as ex:
        print ("Что-то пошло не так! Выполняется выход из программы.")
        print(f"Текст ошибки: {ex}")
    finally:
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Скрипт для скачивания постов с Instagram.')
    parser.add_argument('--nickname', type=str, help='Имя пользователя Instagram, чьи посты будут скачаны в CSV файл')
    parser.add_argument('--browser', type=str, default='chrome', help='Выберите браузер (chrome, firefox, edge или ie)')
    parser.add_argument('--path', type=str, help='Пользовательский путь к браузеру, если он нестандартный')
    
    args = parser.parse_args()
    main(args.nickname, args.browser, args.path)
