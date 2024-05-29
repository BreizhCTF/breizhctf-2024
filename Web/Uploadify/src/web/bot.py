from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from os import environ
import sys


def visit(id):
    url = "http://127.0.0.1/api/download.php?id=" + id
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-jit")
    chrome_options.add_argument("--disable-wasm")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(3)

    try:
        driver.get(url)
        driver.get("http://127.0.0.1/login.php")
        email = driver.find_element(By.ID, "email")
        email.send_keys("admin")
        password = driver.find_element(By.ID, "password")
        password.send_keys(environ["ADMIN_PASSWORD"])
        submit = driver.find_element(By.ID, "submit")
        submit.click()
    except Exception as e:
        print("If this happens in production. Please contact an admin.")

    sleep(3)
    driver.close()

if __name__ == '__main__':
    visit(sys.argv[1])
