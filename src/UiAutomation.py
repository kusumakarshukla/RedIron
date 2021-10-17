from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class BrowserAutomation:
    '''
    @Author : Kusumakar Shukla
    @Functions : getDriver(),resetPassword()
    @version : 1.0
    @since : 1.0
    @Arguments : user email_id
    This class performs the following tasks:
    1. Loads the browser ( Chrome for now).
    2. Navigates to the sign in page and selects "Forgot Password" field.
    3. Prints the Error on Console if the Email is not registered.
    4. Requests barnesandnoble to send the Password Reset link to the registered email ( Preferably Gmail)
    
    '''

    def __init__(self,user_email):
        self.browser = self.getDriver()
        self.email_id = user_email



    def getDriver(self):
       
        driver = webdriver.Chrome(executable_path='libs/chromedriver')
            
        driver.get("https://www.barnesandnoble.com/h/books/browse")
        return driver

    
    def resetPassword(self):
        driver = self.browser
        delay = 20
        account = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/header/nav/div/div[2]/ul[2]/li[1]/a")))
        account.click()
        for button in driver.find_elements_by_tag_name("a"):
                if 'Sign In' in button.text:
                    button.click()
                    break
        login_window = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[6]/div/iframe")))
        driver.switch_to.frame(login_window)
        password_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,"loginForgotPassword")))
        password_link.click()
        driver.switch_to_default_content()
        assistance = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[7]/div/iframe")))
        driver.switch_to.frame(assistance)
        email = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID,"email")))
        email.click()
        email.send_keys(self.email_id)
        submit = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID,"resetPwSubmit")))
        submit.click()
        driver.switch_to_default_content()
        try:

            ifr = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[8]/div/iframe")))
            driver.switch_to.frame(ifr)
            for i in driver.find_elements_by_tag_name("input"):
   
                if i.get_attribute("value")=='Continue':
                    i.click()
                    break
                 
            return None
        except:
            
            driver.switch_to_default_content()
            ifr = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[7]/div/iframe")))
            driver.switch_to.frame(ifr)
            errorItem  = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[2]/aside/em")))
            result =  errorItem.text
            
            return result
        finally:
            driver.close()
        
            
        
        

        
                    



