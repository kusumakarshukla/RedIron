from src.GetGmailMail import ReadGmail
from src.UiAutomation import BrowserAutomation
import os
import sys
def run_app():
    email_id = sys.argv[1]
    print("******* UI AUTOMATION STARTS **********")
    status = BrowserAutomation(email_id).resetPassword()
    if status is not None:
        print(status)
    else:
        print("********** RESET LINK SENT **********")
        results = ReadGmail(email_id).search_messages("barnesandnoble@mail.barnesandnoble.com")   
        print(results)


run_app()