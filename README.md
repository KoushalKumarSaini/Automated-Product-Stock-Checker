🛍️ Automated Amul Whey Protein Stock Checker
This project is a Python-based application designed to automatically monitor the stock status of Amul Whey Protein on the official Amul website.

The script runs a continuous loop that periodically scrapes the product's webpage. If it detects that a previously out-of-stock item has become available, it sends an email notification to the user, ensuring you never miss an opportunity to purchase. This project demonstrates proficiency in automated data collection, backend logic, and integrating external services.

⚙️ Key Features
1. Automated Web Scraping: Uses Selenium and undetected_chromedriver to bypass bot detection and reliably check the product page.

2. Conditional Email Notifications: Sends an email only when the stock status changes from 'sold out' to 'in stock', preventing spam.

3. Data Persistence: Stores the last known stock status in a stock_status.json file to manage conditional alerts.

4. Robustness: Includes error handling for network issues and changes in website structure.

🛠️ Technologies Used
1. Python: The core programming language.

2. Selenium & undetected_chromedriver: For browser automation and web scraping.

3. smtplib: Standard Python library for sending email notifications.

4. JSON: For simple data persistence.

🚀 Getting Started
To run this project locally, follow these steps:

1. Clone the repository:

git clone https://github.com/KoushalKumarSaini/Automated-Product-Stock-Checker.git
cd Automated-Product-Stock-Checker

2. Install dependencies:

pip install -r requirements.txt

3. Configure Email Settings:
Open the check_stock.py file and update the following variables with your own email credentials and the recipient's address. Note: For Gmail, you will need to generate an App Password to use this feature.

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "recipient_email@gmail.com"

4. Run the script:

python check_stock.py

The script will now run in a continuous loop, checking the website every minute. You can stop it at any time by pressing Ctrl + C.

📄 License
This project is licensed under the MIT License.
