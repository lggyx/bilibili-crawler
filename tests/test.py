from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.bilibili.com")
print(driver.title)