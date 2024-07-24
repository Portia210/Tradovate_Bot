import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# set the driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument('--headless')  # Enable headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
chrome_options.add_argument("accept-language=en-US;q=0.8,en;q=0.7")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()


print("please wait for Tradovate login page to load...")
print("----------------------------------------")
driver.get("https://trader.tradovate.com/welcome")
time.sleep(1)
current_url = driver.current_url
username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name-input")))
password = driver.find_element(By.ID, "password-input")
username.send_keys("APEX_85123")
password.send_keys("ARkh@57@Hj@#")

driver.find_element(By.CSS_SELECTOR, ".MuiButton-label").click()
time.sleep(1)
WebDriverWait(driver, 10).until(EC.url_changes(current_url))
current_url = driver.current_url
access_simulation_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiButton-label"))).click()
time.sleep(1)
WebDriverWait(driver, 10).until(EC.url_changes(current_url))
account_info_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".balance-view.dropdown"))).click()
time.sleep(0.2)
panic_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".panic-button")))
panic_btn.click()
time.sleep(0.5)
try:
    dialog_div = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
    try:
        exit_all_btn = dialog_div.find_element(By.CSS_SELECTOR, ".container-fluid").find_element(By.CSS_SELECTOR, ".btn-danger")
        print("closed position")
    except NoSuchElementException:
        try:
            modal_body_text = dialog_div.find_element(By.CSS_SELECTOR, ".modal-body").text
            print(modal_body_text)
        except NoSuchElementException:
            print("something went wrong")

except NoSuchElementException:
    print("no dialog div found")
driver.close()
driver.quit()
