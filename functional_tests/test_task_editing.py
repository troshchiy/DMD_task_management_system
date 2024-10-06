import re
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By

from .base import FunctionalTest


class TaskEditingTest(FunctionalTest):
    def test_can_view_task_details(self):
        # User goes to homepage
        self.browser.get(self.live_server_url)

        # User adds task "Buy tea"
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        buy_tea_task_data = {
            'title': 'Buy tea',
            'description': 'Go to the tea shop and buy puer tea',
            'performers': 'Vladislav Troshchiy',
            'deadline': '2024-10-02 20:00'
        }
        self.add_task(form=add_task_form, **buy_tea_task_data)

        buy_tea_created_at = datetime.now()
        buy_tea_planned_labor_intensity = datetime.strptime(
            buy_tea_task_data['deadline'], '%Y-%m-%d %H:%M'
        ) - buy_tea_created_at.replace(second=0, microsecond=0)

        self.wait_for_item_in_tasks_list('Buy tea')

        # Then user adds task "Brew the tea"
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        brew_the_tea_task_data = {
            'title': 'Brew the tea',
            'description': 'Place 10g of tea into the tea pot and steep tea between 3 to 5 minutes.',
            'performers': 'Vlad Troshchiy',
            'deadline': '2024-10-03 13:00'
        }
        self.add_task(form=add_task_form, **brew_the_tea_task_data)

        brew_the_tea_created_at = datetime.now()
        brew_the_tea_planned_labor_intensity = datetime.strptime(
            brew_the_tea_task_data['deadline'], '%Y-%m-%d %H:%M'
        ) - brew_the_tea_created_at.replace(second=0, microsecond=0)


        self.wait_for_item_in_tasks_list('Brew the tea')

        # User wants to see detail info about the "Buy tea" task, so he hits on the "Brew tea" list item at the sidebar
        buy_tea_li = self.wait_for_item_in_tasks_list('Buy tea')
        buy_tea_li.click()

        # The page shows the "Buy tea" task details including title, description, performers, status, deadline and created date
        self.wait_for(
            lambda: self.assert_task_details_equals_to(
                **buy_tea_task_data,
                created_at=buy_tea_created_at,
                status_label='Assigned',
                planned_labor_intensity=buy_tea_planned_labor_intensity)
        )

        # User noticed that the current URL has changed to my-site.com/tasks/[0-9]*/
        self.wait_for(
            lambda: self.assertTrue(
                re.findall('/tasks/[0-9]+/', self.browser.current_url)
            )
        )
        buy_tea_task_url = self.browser.current_url

        # Then user wants to see detail info about the "Brew the tea" task, and he hits on the list item
        self.wait_for_item_in_tasks_list('Brew the tea').click()

        # And the page shows the detail info
        self.wait_for(
            lambda: self.assert_task_details_equals_to(
                **brew_the_tea_task_data,
                created_at=brew_the_tea_created_at,
                status_label='Assigned',
                planned_labor_intensity=brew_the_tea_planned_labor_intensity
            )
        )

        # And current URL has changed, and now it looks like my-site.com/tasks/2/
        self.wait_for(
            lambda: self.assertNotEqual(    # Wait until current URL changes
                buy_tea_task_url,
                self.browser.current_url
            )
            )

        self.wait_for(
            lambda: self.assertTrue(        # Make sure that the link is in the correct format
                re.findall('/tasks/[0-9]+/', self.browser.current_url)
            )
        )

        # User noticed that now there are no info about the "Buy tea" task
        content = self.browser.find_element(By.ID, 'content')
        self.assertNotIn('Buy tea', content.get_attribute('innerHTML'))
        self.assertNotIn('Go to the tea shop and buy puer tea', content.get_attribute('innerHTML'))
        self.assertNotIn('Vladislav Troshchiy', content.get_attribute('innerHTML'))
        self.assertNotIn('2024-10-02 20:00', content.get_attribute('innerHTML'))

    def test_can_edit_a_task(self):
        # User goes to homepage of the web-application and creates a task
        self.browser.get(self.live_server_url)
        add_task_form = self.wait_for(lambda: self.browser.find_element(By.ID, 'add-task'))
        self.add_task(
            form=add_task_form,
            title='Old title',
            description='Old description',
            performers='Old performers',
            deadline='1999-12-21 17:15'
        )

        # User choose the added task at the sidebar tasks list to open task details
        self.wait_for_item_in_tasks_list('Old title').click()

        task_detail = self.wait_for(lambda: self.browser.find_element(By.ID, 'task-detail'))
        old_task_created_at = task_detail.find_element(By.ID, 'id_created_at').text

        # User decides to change all task details
        # He edits task title, description, performers and deadline
        edit_data = {
            'title': 'New title',
            'description': 'New description',
            'performers': 'New performers',
            'deadline': '2024-10-07 13:00',
            'status_label': 'In progress'
        }

        title_inputbox = task_detail.find_element(By.ID, 'id_title')
        title_inputbox.clear()
        title_inputbox.send_keys(edit_data['title'])

        description_inputbox = task_detail.find_element(By.ID, 'id_description')
        description_inputbox.clear()
        description_inputbox.send_keys(edit_data['description'])

        performers_inputbox = task_detail.find_element(By.ID, 'id_performers')
        performers_inputbox.clear()
        performers_inputbox.send_keys(edit_data['performers'])

        deadline_inputbox = task_detail.find_element(By.ID, 'id_deadline')
        deadline_inputbox.clear()
        deadline_inputbox.send_keys(edit_data['deadline'])

        status_selector = task_detail.find_element(By.ID, 'id_status')
        status_options = status_selector.find_elements(By.TAG_NAME, 'option')
        for option in status_options:
            if option.text == edit_data['status_label']:
                option.click()

        # Then User submit changes via "Save" button
        save_btn = task_detail.find_element(By.CLASS_NAME, 'submit-btn')
        self.assertEqual(save_btn.get_attribute('value'), 'Save')
        save_btn.click()

        edited_task_planned_labor_intensity = (datetime.strptime(edit_data['deadline'], '%Y-%m-%d %H:%M')
                                               - datetime.strptime(old_task_created_at, '%Y-%m-%d %H:%M'))

        # The page updates and now shows new task details, but created_at value hasn't changed
        self.wait_for(
            lambda: self.assert_task_details_equals_to(
                title=edit_data['title'],
                description=edit_data['description'],
                performers=edit_data['performers'],
                deadline=edit_data['deadline'],
                created_at=datetime.strptime(old_task_created_at, '%Y-%m-%d %H:%M'),
                status_label=edit_data['status_label'],
                planned_labor_intensity=edited_task_planned_labor_intensity
            )
        )

        # User notices that there is still only one task at the sidebar tasks list, and it's title has changed too
        tasks_list = self.browser.find_element(By.ID, 'tasks-list')
        items = tasks_list.find_elements(By.CLASS_NAME, 'task-title')
        self.assertEqual(len(items), 1)
        self.assertIn('New title', [item.text for item in items])
        self.assertNotIn('Old title', [item.text for item in items])

        # When user completed has completed the task, he decides to mark it on the site
        task_detail = self.wait_for(lambda: self.browser.find_element(By.ID, 'task-detail'))
        status_options = task_detail.find_element(By.ID, 'id_status').find_elements(By.TAG_NAME, 'option')
        for option in status_options:
            if option.text == 'Completed':
                option.click()

        task_detail.find_element(By.CLASS_NAME, 'submit-btn').click()

        completed_at = datetime.now()
        time_of_completion = completed_at.replace(second=0, microsecond=0) - datetime.strptime(old_task_created_at, '%Y-%m-%d %H:%M')

        # The page updates and now shows new task details: 'Completed at' and 'Actual_time_of_completion'
        actual_completed_at_value = self.wait_for(lambda: self.browser.find_element(By.ID, 'id_completed_at'))
        self.assertAlmostEqual(
            datetime.strptime(actual_completed_at_value.text, '%Y-%m-%d %H:%M'),
            completed_at,
            delta=timedelta(minutes=1)
        )

        actual_time_of_completion = self.wait_for(lambda: self.browser.find_element(By.ID, 'id_actual_completion_time'))
        days = time_of_completion.days
        hours, seconds = divmod(time_of_completion.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        self.assertEqual(
            actual_time_of_completion.text,
            f'{days} days, {hours} hours, {minutes} minutes'
        )
