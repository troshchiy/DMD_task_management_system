import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10

class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def add_task(self, task):
        add_task_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'add-task')
        )
        inputbox = add_task_form.find_element(By.ID, 'id_title')
        inputbox.send_keys(task)
        inputbox.send_keys(Keys.ENTER)

    def wait_for_item_in_tasks_list(self, item_text):
        start_time = time.time()
        while True:
            try:
                tasks_list = self.browser.find_element(By.ID, 'tasks-list')
                items = tasks_list.find_elements(By.TAG_NAME, 'li')
                self.assertIn(item_text, [item.text for item in items])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def get_new_task_title_inputbox(self):
        add_task_form = self.browser.find_element(By.ID, 'add-task')
        return add_task_form.find_element(By.ID, 'id_title')
