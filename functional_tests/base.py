from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def add_task(self, task):
        add_task_form = self.browser.find_element(By.ID, 'add-task')
        inputbox = add_task_form.find_element(By.ID, 'id_title')
        inputbox.send_keys(task)
        inputbox.send_keys(Keys.ENTER)
