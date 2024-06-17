'''
Example to use Selenium to scrape the course description of a course in NTU.
There is a better way by using the POST API, so this script is not used now.
Just putting it here for reference in case it is needed in the future.
'''
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


driver = Chrome()

try:
    # open the url available to public
    driver.get("https://wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main")

    # select the correct acadsem from the select element
    acadsem_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "acadsem"))
    )
    acadsem_select.find_element(By.CSS_SELECTOR, "option[value='2023_2']").click()

    # select the corresponding course code (in reality you want to loop through all the course codes)
    r_subj_code_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "r_subj_code"))
    )
    r_subj_code_input.send_keys("MH1101")

    # click on the search button
    search_button = driver.find_element(By.CSS_SELECTOR, "input[value='Search']")
    search_button.click()

    # wait for the iframe to be present, parse the HTML content
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)
    iframe_content = driver.page_source
    soup = BeautifulSoup(iframe_content, 'html.parser')

    # find last td that contains course description
    course_description_td = soup.find_all('td')[-2]
    course_description = course_description_td.get_text(strip=True)

    # perform operation on the course description...
    print(course_description)

finally:
    # wait for 10secs so we can see the result
    time.sleep(10)
    driver.quit()
