from django.test import TestCase, Client
from django.urls import reverse


class AboutViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()

    def test_pages_use_correct_template(self):
        templates_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class AboutUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()

    def test_urls_use_correct_templates(self):
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_avaliable_for_everyone(self):
        response_status_code = {
            'about:author': 200,
            'about:tech': 200,
        }
        for template, status_code in response_status_code.items():
            with self.subTest():
                response = self.client.get(reverse(template))
                self.assertEqual(response.status_code, status_code)
