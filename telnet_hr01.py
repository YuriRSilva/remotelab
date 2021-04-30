from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

onu_url = 'http://192.168.101.1'
username = 'admin'
password = 'admin'

driver = webdriver.Chrome()
driver.get(onu_url)

# Pagina de login
user_field = driver.find_element_by_name('username')
pass_field = driver.find_element_by_id('password')
login_button = driver.find_element_by_id('Login')
user_field.send_keys(username)
pass_field.send_keys(password)
login_button.click()

# Altera para o Iframe do menu
iframe1 = driver.find_element_by_xpath("//iframe[@id='menu_page']")
driver.switch_to.frame(iframe1)

# Navega pelo Iframe do menu para chegar abrir a pagina de segurança/serviço
menu_security = driver.find_element_by_id('menu_security')
menu_security.click()
submenu_service = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'submenu_service')))
iframe2 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'main_page_select')))

while True:
    try:
        submenu_service.click()
        driver.switch_to.frame(iframe2)
        new_sec_rule_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'servicecontrol_newbutton')))
        new_sec_rule_button.click()
    except TimeoutException or NoShuchElementException:
        driver.switch_to.frame(iframe1)
        pass
    else:
        print('Pagina Security/Service carregada')
        break

active_chkbtn = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'servicecontrol_active_chkbtn')))
startip_field = driver.find_element_by_name('servicecontrol_startip')
endip_field = driver.find_element_by_name('servicecontrol_endip')

startip_field.send_keys('192.168.101.2')
endip_field.send_keys('192.168.101.254')

select_mode = Select(driver.find_element_by_id('servicecontrol_mode'))
elect_mode.select_by_visible_text('Permit')

telnet_chkbox = driver.find_element_by_id('servicelist_telnet')
telnet_chkbox.click()

apply_btn = driver.find_element_by_id('Apply_button')
apply_btn.click()
