from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

# Path to your Excel file
file_path = "path/to/your/excel_file.xlsx"

# Read the Excel file into a DataFrame
df = pd.read_excel(file_path)

# Get the last column (assuming no headers or named columns)
last_column = df.iloc[:, -1]

# Loop through each item in the last column
for item in last_column:
  # Do something with the item (e.g., print it)
  print(item)

for i in u:
    # Replace with the URL of the website you want to open
    website_url = i

    # Replace with the text of the link you want to click
    link_text = "Published Report"

    # Path to your webdriver (e.g., chromedriver.exe for Chrome)
    webdriver_path = "chromedriver.exe"

    # Initialize the webdriver (download and configure accordingly)
    driver = webdriver.Chrome(executable_path=webdriver_path)

    # Open the website
    driver.get(website_url)

    # Wait for the link element to be clickable
    link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, link_text))
    )

    # Click on the link
    link.click()

    # Wait for the new page to load (adjust timeout if needed)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Get the current URL of the loaded page
    current_url = driver.current_url

    # Print the copied link
    print(f"Copied link: {current_url}")

    # Close the browser window (optional)
    driver.quit()