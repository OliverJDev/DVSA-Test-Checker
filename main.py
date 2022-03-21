from selenium import webdriver
from datetime import datetime
import winsound

import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from plyer import notification
import smtplib

#Sends an email to a gmail account notifying of a test avaliable
def sendEmail(string):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login("<email>", "<password>")

    # message to be sent
    message = string

    # sending the mail
    s.sendmail("<email>", "<email>, message)


details = {
    "Licence": "<uk license>",  # Full UK Licence
    "Booking_Ref": "<current booking ref>",  # Test Booking Refrence
    "Test_Center": ["<test center>", "<test center>"],  # Name of Test Center
    "before_date": "2021-12-02"
}

smtp = {
    "sender": "<email>",  # SMTP sender address
    "sender_title": "DVSA Test Check",  # SMTP sender name
    "recipient": ["<email>"],  # Notification recipient
    "server": "smtp.example.com",  # SMTP server address
    "login": "<email>",  # SMTP server login
    "password": "<email password>"  # SMTP server password
}

import time

#A constant loop that checkers every so often for a test by looping through dates and performing checks to see whether a test is avaliable before the before_date variable
while True:
    driver = webdriver.Chrome()
    # Open the test booking management website
    driver.get('https://driverpracticaltest.dvsa.gov.uk/login')

    currentURL = driver.current_url
    while 'queue' in currentURL:
        currentURL = driver.current_url

    # Login with current test details
    driver.find_element_by_id("driving-licence-number").send_keys(details["Licence"])

    driver.find_element_by_id("application-reference-number").send_keys(details["Booking_Ref"])

    driver.find_element_by_id("booking-login").click()

    f = open("tests.txt", "w")
    f.write("Available Tests")
    driver.find_element_by_id("test-centre-change").click()

    for test in details["Test_Center"]:
        print("----")
        print(test)
        driver.find_element_by_id("test-centres-input").clear()
        driver.find_element_by_id("test-centres-input").send_keys(test)

        driver.find_element_by_id("test-centres-submit").click()

        # Select first test center
        try:
            results_container = driver.find_element_by_class_name("test-centre-results")
        except:
            results_container = driver.find_element_by_class_name("test-centre-results")

        test_center = results_container.find_element_by_xpath(".//a")

        test_center.click()

        # Check if any tests avaliable
        if "There are no tests available" in driver.find_element_by_id("main").get_attribute('innerHTML'):
            print("No tests available...")
            f.write("\n" + test + ": No Tests")
            driver.execute_script("window.history.go(-1)")
        else:
            print("Tests available, checking dates...")



            minDate = datetime.strptime(details["before_date"], "%Y-%m-%d")
            available_calendar = driver.find_element_by_class_name("BookingCalendar-datesBody")
            available_days = available_calendar.find_elements_by_xpath(".//td")
            available_days_msg = ""

            for day in available_days:
                if not "--unavailable" in day.get_attribute("class"):
                    day_a = day.find_element_by_xpath(".//a")
                    f.write("\n" + test + ": " + day_a.get_attribute("data-date"))
                    date = datetime.strptime(day_a.get_attribute("data-date"), "%Y-%m-%d")
                    print(date)
                    if date.month != 7:
                        print('NEW TEST AVAILABLE - ' + test + " - " + day_a.get_attribute("data-date"))
                        sendEmail('NEW TEST AVAILABLE - ' + test + " - " + day_a.get_attribute("data-date"))
                        # loop iterates 5 times i.e, 5 beeps will be produced.
                        freq = 100
                        dur = 50
                        for i in range(0, 55):
                            winsound.Beep(freq, dur)
                            freq += 100
                            dur += 50
                    driver.execute_script("window.history.go(-1)")
                    break
    print("Ending and Saving to file")
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    f.write("\n\nUpdated: " + dt_string)
    f.close()
    driver.quit()
    time.sleep(60 * 6)
