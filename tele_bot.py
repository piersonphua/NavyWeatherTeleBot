from telegram import Bot
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
import time
import random
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import asyncio
from io import BytesIO

load_dotenv()
your_bot_token = os.getenv("BOT_TOKEN")

## Create a new Chrome browser instance
chrome_options = Options()
chrome_options.add_argument("--headless") 
driver = webdriver.Chrome(options=chrome_options)

## Function to extract table data
def extract_table_data(xpath):
    table = driver.find_element(By.XPATH, xpath)
    rows = table.find_elements(By.TAG_NAME, 'tr')
    data = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in rows]
    return data

# Navigate to the website
driver.get('https://www.weather.gov.sg/wip-login.php')

###Sleep for 5 seconds
time.sleep(5)

# Locate fields and button
username_field = driver.find_element(By.ID, "user_login")
password_field = driver.find_element(By.ID, "pwd")
login_button = driver.find_element(By.ID, "wp-submit")

# Enter credentials
username_field.click()
username_field.send_keys(os.getenv("USER"))
password_field.click()

for character in os.getenv("PW"):
    password_field.send_keys(character)
    time.sleep(random.uniform(0.1, 0.3))

login_button.click()

# Sleep for 15 seconds
time.sleep(15)

# XPaths dictionary
xpaths = {
    'local_LEFT_col': '//*[@id="tableData"]/div[2]/table[1]/tbody',
    'local_RIGHT_col': '//*[@id="tableData"]/div[3]/table/tbody',
    'four_day_outlook': '//*[@id="tableData"]/div[1]/div[3]/table[1]/tbody',
    'monthly_outlook': '//*[@id="tableData"]/div[1]/div[3]/table[3]/tbody'
}

# Extract local waters table data
daily_outlook_data = extract_table_data(xpaths['local_LEFT_col']) + extract_table_data(xpaths['local_RIGHT_col'])

# Locate haze outlook link and click
try:
    haze_outlook_link = driver.find_element(By.XPATH, "//*[contains(text(),'Weather Outlook on Current Haze Situation - Singapore')]")
except NoSuchElementException:
    haze_outlook_link = driver.find_element(By.XPATH, '/html/body/div/div/ul/li[5]/a')
haze_outlook_link.click()

# Sleep for 15 seconds
time.sleep(15)

# Extract haze outlook table data
four_day_outlook_data = extract_table_data(xpaths['four_day_outlook'])
monthly_outlook_data = extract_table_data(xpaths['monthly_outlook'])

# Extract data
Singapore_Outlook = driver.find_element(By.XPATH, '//*[@id="tableData"]/div[1]/div[2]/table[1]/tbody/tr/td/p').text
Remarks = driver.find_element(By.XPATH, '//*[@id="tableData"]/div[1]/div[2]/table[3]/tbody/tr/td/p').text

# Extract list items
fortnightly_weather_outlook_items = driver.find_elements(By.XPATH, '//*[@id="tableData"]/div[1]/div[3]/table[2]/tbody/tr/td/ul/li')
fortnightly_outlook_data = [item.text for item in fortnightly_weather_outlook_items]

# Close the browser
driver.quit()

# Store the data
Singapore_Outlook = '<b><u>Singapore Outlook</u></b>\n' + Singapore_Outlook
Remarks = '<b><u>Remarks</u></b>\n' + Remarks
fortnightly_outlook_data = '<b><u>Fortnightly Outlook Data</u></b>\n' + '\n'.join('- ' + line for line in fortnightly_outlook_data)

# Create a dictionary to hold pandas dataframes
data_frames = {}
# Convert your list data into pandas dataframes and store in the dictionary
data_frames["daily_outlook_data"] = pd.DataFrame(daily_outlook_data)
data_frames["four_day_outlook_data"] = pd.DataFrame(four_day_outlook_data)
data_frames["monthly_outlook_data"] = pd.DataFrame(monthly_outlook_data)

# Filter the first dataframe
data_frames["daily_outlook_data"] = data_frames["daily_outlook_data"][data_frames["daily_outlook_data"].iloc[:, 0] != 'Area of interest']

# Create a BytesIO object
output = BytesIO()

# Create a Pandas Excel writer using openpyxl as the engine
writer = pd.ExcelWriter(output, engine='openpyxl')

# Write each DataFrame to an Excel sheet
for name, df in data_frames.items():
    df.to_excel(writer, sheet_name=name, index=False)

# Save the Excel file
writer.close()

output.seek(0)
book = load_workbook(output)

for sheet in book:
    for column_cells in sheet.columns:
        sheet.column_dimensions[column_cells[0].column_letter].width = 25
        for cell in column_cells:
            cell.alignment = Alignment(wrapText=True)
output = BytesIO()
book.save(output)

# Go to the start of the BytesIO object
output.seek(0)

today = datetime.now()+timedelta(days=1)

today = today.strftime("%d0630H %B %Y") # e.g., 270630H May 2023

async def main():
    chat_id = os.getenv("CHAT_ID")
    bot = Bot(token=your_bot_token)
    text1 = Singapore_Outlook
    text2 = Remarks
    text3 = fortnightly_outlook_data
    table = output
    await bot.send_message(chat_id=chat_id, text=text1, parse_mode = 'HTML')
    await bot.send_message(chat_id=chat_id, text=text2, parse_mode = 'HTML')
    await bot.send_message(chat_id=chat_id, text=text3, parse_mode = 'HTML')
    await bot.send_document(chat_id=chat_id, document = table, filename= f'Data CAA {today}.xlsx')

# Run the main function
asyncio.run(main())
