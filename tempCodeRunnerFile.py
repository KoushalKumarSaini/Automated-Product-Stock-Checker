from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import undetected_chromedriver as uc
import time
import smtplib
from email.mime.text import MIMEText
import os 

# --- SCRIPT CONFIGURATION ---
# URL of the product
PRODUCT_URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-30-sachets"

# Email settings
SENDER_EMAIL = "koushalsaini54@gmail.com"
SENDER_PASSWORD = "odta mwhc quzl xypy" # Use the app password you generated here
RECEIVER_EMAIL = "ypmyogeshwar8080@gmail.com"
EMAIL_SUBJECT = "AMUL PRODUCT BACK IN STOCK!"

# --- EMAIL NOTIFICATION FUNCTION ---
def send_email_notification():
    """
    Sends a stock alert email.
    """
    msg = MIMEText(f"The Amul product is back in stock! Buy it now at: {PRODUCT_URL}")
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email notification sent!")
    except Exception as e:
        print(f"💥 Failed to send email: {e}")

# --- WEB SCRAPING FUNCTION ---
def check_stock_status():
    """
    Checks the stock status and returns 'in_stock', 'out_of_stock', or 'error'.
    """
    options = Options()
    
    # Using undetected_chromedriver to bypass Cloudflare, so fewer arguments are needed
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')

    # You can change the headless mode for local debugging
    # options.add_argument('--headless=new')
    
    try:
        # undetected_chromedriver automatically handles the driver and uses a human-like user agent
        driver = uc.Chrome(use_subprocess=True, options=options)
    except Exception as e:
        print(f"💥 Failed to set up Chrome driver with undetected_chromedriver: {e}")
        return "error"
    
    try:
        print("🚀 Opening product page...")
        driver.get(PRODUCT_URL)

        print("⏳ Waiting for pincode modal...")
        modal_dialog = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "locationWidgetModal"))
        )

        pincode_input = modal_dialog.find_element(By.ID, "search")
        print("📍 Entering pincode...")
        pincode_input.send_keys("560102")
        
        print("🔎 Waiting for pincode suggestions...")
        retries = 3
        while retries > 0:
            try:
                pincode_suggestion = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'searchitem-name') and .//p[contains(text(), '560102')]]"))
                )
                driver.execute_script("arguments[0].click();", pincode_suggestion)
                print("✅ Successfully clicked the pincode suggestion.")
                break
            except StaleElementReferenceException:
                print(f"⚠️ Stale element detected. Retrying... ({retries-1} attempts left)")
                retries -= 1
                time.sleep(2)
            except Exception as e:
                raise e
        
        if retries == 0:
            raise Exception("Failed to click pincode suggestion after multiple retries.")
        
        time.sleep(5) 
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger') and contains(text(), 'Sold Out')]"))
            )
            print("❌ Product is SOLD OUT.")
            return "out_of_stock"
        except TimeoutException:
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'cart-button-text') and contains(text(), 'Add to cart')]"))
            )
            print("✅ Product is IN STOCK! Go grab it now.")
            return "in_stock"
        
    except Exception as e:
        print(f"💥 Unexpected error during scraping: {e}")
        return "error"
    finally:
        driver.quit()

# --- MAIN LOOP ---
def handler(event, context):
    """This function is the entry point for AWS Lambda."""
    status = check_stock_status()
    if status == "in_stock": # Only send email if product is in stock
        send_email_notification()
    return {
        'statusCode': 200,
        'body': f'Script ran and found status: {status}'
    }

if __name__ == "__main__":
    while True:
        status = check_stock_status()
        if status == "in_stock": # Only send email if product is in stock
            send_email_notification()
            print("The product status has changed from 'Sold Out'! Exiting the script.")
            break
        
        print(f"Status: {status}. Waiting 1 minute before checking again...")
        time.sleep(60)
