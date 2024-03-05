from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TEMPLATES_URL_NAMES = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.."""
        for template, address in self.TEMPLATES_URL_NAMES.items():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
