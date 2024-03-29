'''
This surfs San Mateo's https://webschedule.smccd.edu/ website
and gets all the class information for the curent semester
at Skyline.
Takes a minute to run the first time on a new day.
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import datetime
import pickle

import pandas as pd

# Get all Skyline classes for correct term from Webschedule website
def get_webschedule_classes():
    # Use selenium webdriver to get the current url of page with all Skyline classes
    # Set up options arguments for selenium webdriver
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    webschedule_url = "https://webschedule.smccd.edu/"

    driver.get(webschedule_url)

    # Select html radio button for current semester at Skyline
    # If month is July or later, it is Fall semester. Otherwise, Spring
    # **Summer in future??
    month = datetime.datetime.now().month
    if month >= 7:
        # Fall Semester
        radio = driver.find_element('xpath', '''//*[@id="default"]/div[1]/div/fieldset/div/label[1]''')
        radio.click()

    # Uncheck Cañada
    radio = driver.find_element('xpath', '''//*[@id="default"]/div[3]/div/fieldset/label[1]/input''')
    radio.click()

    # Uncheck CSM. Leave Skyline checked
    radio = driver.find_element('xpath', '''//*[@id="default"]/div[3]/div/fieldset/label[2]/input''')
    radio.click()

    # Click "Search All" button to get page of all classes for Skyline
    search = driver.find_element('xpath', '''//*[@id="default"]/div[2]/div/div/div/button[1]''')
    search.click()

    # All this to get the url!
    webschedule_url = driver.current_url

    r = requests.get(webschedule_url).text
    soup = BeautifulSoup(r, 'html.parser')

    classes = {}

    crn_list = []
    course_title_list = []
    units_list = []
    days_list = []
    instructor_list = []
    meeting_date_list = []
    meeting_time_list = []

    # Html element with all subjects & classes
    subjects = soup.find_all('div', class_='list')

    for subject in subjects:
        # Each subject in list of all subjects
        classes_ = subject.table.tbody.find_all('tr')
        
        for class_ in classes_:
            # Each class in list of all classes
            
            # List of attributes for each class
            td = class_.find_all('td')
            
            crn          = td[2].text.strip()
            # Course_title may not exist
            course_title = ''
            try:
                course_title = td[3].a.text.strip()
            except:
                pass
            units        = td[4].text.strip()
            days         = td[5].text.strip()
            instructor   = td[6].text.strip()
            meeting_date = td[7].text.strip()
            meeting_time = td[8].text.strip()
            
            # Add to each list
            crn_list.append(crn)
            course_title_list.append(course_title)
            units_list.append(units)
            days_list.append(days)
            instructor_list.append(instructor)
            meeting_date_list.append(meeting_date)
            meeting_time_list.append(meeting_time)

    # Populate dictionary of classes to turn into DataFrame
    classes['CRN'] = crn_list
    classes['Course Title'] = course_title_list
    classes['Units'] = units_list
    classes['Days'] = days_list
    classes['Instructor'] = instructor_list
    classes['Meeting Date'] = meeting_date_list
    classes['Meeting Time'] = meeting_time_list

    # Construct DataFrame of classes
    webschedule_df = pd.DataFrame(classes)
    return webschedule_df


def main():
    # Pickle in (retrieve from .pickle file) dictionary of INFO
    pickle_in = open("webschedule_df.pkl", "rb")
    INFO = pickle.load(pickle_in)

    dt = datetime.datetime.now()
    date = dt.date()
    
    pd.set_option('display.max_rows', 10000)
    pd.set_option('display.max_columns', 10000)
    
    # If program was not run today, get live class info with web scraper
    if INFO['date_today'] != date:
        webschedule_df = get_webschedule_classes()
        
        INFO['date_today'] = date
        INFO['webschedule_df'] = webschedule_df

        pickle_out = open("webschedule", "wb")
        pickle.dump(INFO, pickle_out)
        pickle_out.close()
    else:
        # Else use saved dataframe
        webschedule_df = INFO['webschedule_df']
        
    print(webschedule_df)
    
    
if __name__ == '__main__':
    main()