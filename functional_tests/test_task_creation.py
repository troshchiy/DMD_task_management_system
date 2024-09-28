import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class NewVisitorTest(FunctionalTest):
    def test_can_create_a_task(self):
        # User goes to homepage of the task management web-application
        self.browser.get(self.live_server_url)

        # User noticed that the page title and header mention the task management web-application
        self.assertIn('Tasks', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('Tasks', header_text)

        # The website offers to enter a task
        inputbox = self.browser.find_element(By.ID, 'id_title')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Title'
        )

        # User types "Buy tea"
        inputbox.send_keys('Buy tea')

        # When user hits enter, the page update, and now the page contains "Buy tea" as an item in a tasks lists
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        list_items = tasks_list.find_elements(By.TAG_NAME, 'li')
        self.assertIn('Buy tea', [item.text for item in list_items])

        # There is still a text box inviting user to add another item
        # User enters "Brew the tea"
        inputbox = self.browser.find_element(By.ID, 'id_title')
        inputbox.send_keys("Brew the tea")
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both items on user's list
        time.sleep(1)
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        list_items = tasks_list.find_elements(By.TAG_NAME, 'li')
        items_text = [item.text for item in list_items]
        self.assertIn('Buy tea', items_text)
        self.assertIn('Brew the tea', items_text)