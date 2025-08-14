import smtplib
from email.mime.text import MIMEText
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import os
import json

# --- ENHANCED ERROR HANDLING FOR ENVIRONMENT VARIABLES ---
try:
    from dotenv import load_dotenv
    # Load environment variables from the .env file
    load_dotenv()

    # Email settings from environment variables
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
    
except ImportError:
    print("💥 FATAL ERROR: The 'python-dotenv' library is not installed.")
    print("Please run 'pip install python-dotenv' in your terminal and try again.")
    exit()
except Exception as e:
    print(f"💥 An unexpected error occurred while loading environment variables: {e}")
    print("Please check your .env file for any syntax errors.")
    exit()

# --- SCRIPT CONFIGURATION ---
PRODUCT_URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-30-sachets"

# --- VALIDATE ENVIRONMENT VARIABLES ---
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    print("FATAL ERROR: One or more environment variables (SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL) are not set.")
    print("This is usually because the .env file is missing, misnamed, or its contents are incorrect.")
    print("Please ensure you have a file named '.env' in the same directory as this script.")
    print("The contents should be in the format: VARIABLE_NAME='value'")
    exit()

EMAIL_SUBJECT_IN_STOCK = "AMUL PRODUCT IS NOW IN STOCK!"
EMAIL_SUBJECT_OUT_OF_STOCK = "AMUL PRODUCT IS NOW SOLD OUT!"

# State file to store the last known status
STATUS_FILE = "stock_status.json"

# --- HELPER FUNCTIONS FOR STATE MANAGEMENT ---
def read_last_status():
    """Reads the last known status and email flag from a file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Corrupted status file, starting fresh.")
                return {"status": None, "sold_out_email_sent": False}
    return {"status": None, "sold_out_email_sent": False}

def save_current_status(status_obj):
    """Saves the current status object to a file."""
    with open(STATUS_FILE, "w") as f:
        json.dump(status_obj, f)

# --- EMAIL NOTIFICATION FUNCTIONS ---
def send_in_stock_notification():
    """Sends a stock alert email."""
    print("📧 Attempting to send 'In Stock' email...")
    msg = MIMEText(f"The Amul product is back in stock! Buy it now at: {PRODUCT_URL}")
    msg["Subject"] = EMAIL_SUBJECT_IN_STOCK
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 'In Stock' email notification sent successfully!")
    except Exception as e:
        print(f"💥 Failed to send 'in stock' email: {e}")

def send_sold_out_notification():
    """Sends a sold out email."""
    print("📧 Attempting to send 'Sold Out' email...")
    msg = MIMEText(f"The Amul product is now sold out. It was last seen at: {PRODUCT_URL}")
    msg["Subject"] = EMAIL_SUBJECT_OUT_OF_STOCK
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 'Sold Out' email notification sent successfully!")
    except Exception as e:
        print(f"💥 Failed to send 'sold out' email: {e}")

# --- WEB SCRAPING FUNCTION ---
def check_stock_status():
    """
    Checks the stock status and returns 'in_stock', 'out_of_stock', or 'unknown'.
    """
    print("--- Starting Stock Check ---")
    options = uc.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    driver = None
    try:
        print("⏳ Launching undetected Chrome browser...")
        driver = uc.Chrome(options=options)
        print("✅ Browser launched successfully!")
        
        print("🚀 Opening product page...")
        driver.get(PRODUCT_URL)
        time.sleep(5)
        print("✅ Page loaded. Beginning search for elements...")
        
        # --- ROBUST PINCODE HANDLING ---
        try:
            print("⏳ Waiting for pincode modal to appear...")
            modal_dialog = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "locationWidgetModal"))
            )

            print("📍 Entering pincode...")
            pincode_input = WebDriverWait(modal_dialog, 10).until(
                EC.visibility_of_element_located((By.ID, "search"))
            )
            pincode_input.send_keys("560102")
            
            print("🔎 Waiting for pincode suggestions and clicking...")
            pincode_suggestion = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., '560102')]"))
            )
            pincode_suggestion.click()
            print("✅ Successfully clicked the pincode suggestion.")
            
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.ID, "locationWidgetModal"))
            )
            print("✅ Pincode modal has closed.")

            print("Waiting for product page to refresh...")
            time.sleep(5) 
        except TimeoutException:
            print("⚠️ Pincode modal did not appear or was not found within the timeout. Continuing...")
        except Exception as e:
            print(f"⚠️ An unexpected error occurred with the pincode modal: {e}")

        # Check for the stock status after the pincode is handled
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger') and contains(text(), 'Sold Out')]"))
            )
            print("❌ Product is SOLD OUT.")
            return "out_of_stock"
        except TimeoutException:
            try:
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'cart-button-text') and contains(text(), 'Add to cart')]"))
                )
                print("✅ Product is IN STOCK! Go grab it now.")
                return "in_stock"
            except TimeoutException:
                print("❓ Could not determine stock status. The page structure might have changed.")
                return "unknown"
            
    except WebDriverException as e:
        print(f"💥 FATAL ERROR: Failed to start the WebDriver. This is often due to a browser version mismatch, or Chrome not being installed correctly.")
        print(f"Details: {e}")
        return "error"
    except Exception as e:
        print(f"💥 Unexpected error during scraping: {e}")
        return "error"
    finally:
        if driver:
            try:
                print("--- Stock Check Finished. Closing browser. ---")
                driver.quit()
            except Exception as e:
                print(f"⚠️ Failed to quit the driver, it may have already closed: {e}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    print("--- Stock Checker Initializing ---")
    status_obj = read_last_status()

    while True:
        current_status = check_stock_status()

        if current_status == "out_of_stock":
            if not status_obj.get("sold_out_email_sent"):
                send_sold_out_notification()
                status_obj["sold_out_email_sent"] = True
            
            # Update the status in the file
            status_obj["status"] = "out_of_stock"
            save_current_status(status_obj)
            print("Product is still sold out. Waiting for a change.")

        elif current_status == "in_stock":
            if status_obj["status"] == "out_of_stock":
                send_in_stock_notification()
            
            # Reset the sold out email flag if it's in stock
            status_obj["sold_out_email_sent"] = False
            status_obj["status"] = "in_stock"
            save_current_status(status_obj)
            print("Product is in stock! If it was previously sold out, an email was sent.")

        else: # Handles "unknown" or "error" status
            print(f"Could not determine status: {current_status}. Keeping last status as is.")

        print("Waiting 1 minute for the next check...")
        time.sleep(60) # Wait for 1 minute
