import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException

MAX_WAIT = 10

class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def add_task(self, form, title, description, performers, deadline):
        title_inputbox = form.find_element(By.ID, 'id_title')
        title_inputbox.send_keys(title)

        description_inputbox = form.find_element(By.ID, 'id_description')
        description_inputbox.send_keys(description)

        performers_inputbox = form.find_element(By.ID, 'id_performers')
        performers_inputbox.send_keys(performers)

        deadline_inputbox = form.find_element(By.ID, 'id_deadline')
        deadline_inputbox.send_keys(deadline)

        title_inputbox.send_keys(Keys.ENTER)

    def wait_for_item_in_tasks_list(self, item_text):
        start_time = time.time()
        while True:
            try:
                tasks_list = self.browser.find_element(By.ID, 'tasks-list')
                items = tasks_list.find_elements(By.CLASS_NAME, 'task-title')

                for item in items:
                    if item.text == item_text:
                        return item

                self.fail(f'{item_text} not found in {[item.text for item in items]}')
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

    def get_new_task_element_by_id(self, element_id):
        add_task_form = self.wait_for(
            lambda: self.browser.find_element(By.ID, 'add-task')
        )
        return add_task_form.find_element(By.ID, element_id)
