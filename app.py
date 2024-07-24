import smtplib
import time
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import schedule
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from accounts import accounts

# SMTP email configuration for Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = 'yybarhen@gmail.com'



def send_error_email(subject, message, email_to=EMAIL_TO):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = email_to
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, email_to, msg.as_string())
        server.quit()
        print("Error email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def run_script():
    driver = None
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        chrome_options.add_argument("accept-language=en-US;q=0.8,en;q=0.7")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')  # Usually recommended for headless mode
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--proxy-server="direct://"')
        chrome_options.add_argument('--proxy-bypass-list=*')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--log-level=1')  # Set log level (1 = INFO, 0 = DEBUG)
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--v=1')
        driver = webdriver.Chrome(options=chrome_options)

        # driver.maximize_window()
        driver.get("https://trader.tradovate.com/welcome")

        for account in accounts:
            try:
                # print("Please wait for the Tradovate login page to load...")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name-input")))

                # Enter login credentials
                username = driver.find_element(By.ID, "name-input")
                password = driver.find_element(By.ID, "password-input")
                username.send_keys(account["username"])
                password.send_keys(account["password"])
                driver.find_element(By.CSS_SELECTOR, ".MuiButton-label").click()

                # Wait for the login process to complete and check URL change
                current_url = driver.current_url
                WebDriverWait(driver, 40).until(EC.url_changes(current_url))

                # Click the "Access Simulation" button and check URL change
                current_url = driver.current_url
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiButton-label"))).click()
                WebDriverWait(driver, 10).until(EC.url_changes(current_url))

                # Open the account information dropdown
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".balance-view.dropdown"))).click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".panic-button"))).click()

                # Handle the dialog
                dialog_div = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='dialog']")))
                try:
                    exit_all_btn = dialog_div.find_element(By.CSS_SELECTOR, ".container-fluid").find_element(
                        By.CSS_SELECTOR, ".btn-danger")
                    exit_all_btn.click()
                    send_error_email("Tradovate Crawler", "Closed all positions", email_to=account["email"])
                except NoSuchElementException:
                    modal_body_text = dialog_div.find_element(By.CSS_SELECTOR, ".modal-body").text
                    print(modal_body_text)
                    dialog_div.find_element(By.CSS_SELECTOR, ".btn-primary").click()
                    if "No working orders" not in modal_body_text:
                        send_error_email("Tradovate Crawler Script Error",
                                         "Couldn't find the 'Closed Position' button or 'No positions found' text",
                                         email_to=account["email"])
                time.sleep(0.3)
                account_selector_dropdown = driver.find_element(By.CSS_SELECTOR, ".account-selector.dropdown")
                account_selector_dropdown.click()
                current_url = driver.current_url
                time.sleep(0.3)
                log_outs = driver.find_elements(By.CSS_SELECTOR, ".account.logout")
                log_outs[1].click()
                WebDriverWait(driver, 10).until(EC.url_changes(current_url))

            except Exception as e:
                error_details = traceback.format_exc()
                print(f"Selenium Script Error: An error occurred: {error_details}")
                send_error_email("Tradovate Positions Closer Script Error", f"An error occurred:\n{error_details}",
                                 email_to=account["email"])

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Critical Error: Unable to start the Selenium driver: {error_details}")
        send_error_email("Critical Error: Selenium Driver", f"Unable to start the Selenium driver:\n{error_details}")

    finally:
        if driver:
            driver.quit()


# Schedule the daily task at 10:30 AM every day
schedule.every().day.at("23:00").do(run_script)

# Run the schedule in a loop
while True:
    schedule.run_pending()
    time.sleep(1)
