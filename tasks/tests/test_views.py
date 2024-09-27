from django.test import TestCase
from tasks.models import Task


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'tasks/home.html')

    def test_can_save_a_POST_request(self):
        self.client.post('/', data={'title': 'A new task'})

        self.assertEqual(Task.objects.count(), 1)
        new_task = Task.objects.first()
        self.assertEqual(new_task.title, 'A new task')

    def test_redirects_after_POST(self):
        response = self.client.post('/', data={'title': 'A new task'})
        self.assertRedirects(response, '/')
