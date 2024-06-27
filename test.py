from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

filename = r"C:\Users\JoaquimFrancalanci\OneDrive - ITS Angelo Rizzoli\Desktop\Progetti\Project Work\CIR_Ingredients_Report.xlsx"
df = pd.read_excel(filename)
last_column = df.iloc[:, -1]

for item in last_column:
    website_url = item
    link_text = "Published Report"
    webdriver_path = "chromedriver.exe"
    driver = webdriver.Chrome(executable_path=r"C:\Chrome\chromedriver.exe")
    driver.get(website_url)
    link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, link_text))
    )
    link.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    current_url = driver.current_url
    
    df['extracted links'] = current_url
    df.to_excel(filename, index=False)
    driver.quit()
