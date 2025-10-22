from django.test import TestCase, Client
from django.urls import reverse
from explore_gunung.models import Gunung
import uuid

class ExploreGunungViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.g1 = Gunung.objects.create(
            nama="Gunung Merapi",
            ketinggian=2930,
            provinsi="Yogyakarta",
            foto="https://example.com/merapi.jpg",
            deksripsi="Gunung aktif di Jawa Tengah dan DIY"
        )
        self.g2 = Gunung.objects.create(
            nama="Gunung Bromo",
            ketinggian=2329,
            provinsi="Jawa Timur",
            foto="https://example.com/bromo.jpg",
            deksripsi="Gunung berapi di Jawa Timur"
        )

    def test_show_json_without_query(self):
        response = self.client.get(reverse('explore_gunung:show_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 2)
        self.assertFalse(data['has_more'])

    def test_show_json_with_query_filter(self):
        response = self.client.get(reverse('explore_gunung:show_json') + '?q=merapi')
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['nama'], 'Gunung Merapi')

    def test_show_json_with_pagination(self):
        for i in range(3, 10):
            Gunung.objects.create(
                nama=f"Gunung{i}",
                ketinggian=1000 + i,
                provinsi="Sumatra",
                foto="https://example.com/test.jpg",
                deksripsi="Gunung lain"
            )

        response = self.client.get(reverse('explore_gunung:show_json') + '?page=1&limit=6')
        data = response.json()
        self.assertEqual(len(data['results']), 6)
        self.assertTrue(data['has_more'])

        response = self.client.get(reverse('explore_gunung:show_json') + '?page=2&limit=6')
        data = response.json()
        self.assertLessEqual(len(data['results']), 6)
        self.assertFalse(data['has_more'])

    def test_show_gunung_valid(self):
        url = reverse('explore_gunung:show_gunung', args=[self.g1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.g1.nama)

    def test_show_gunung_not_found(self):
        fake_uuid = uuid.uuid4()  # UUID valid tapi tidak ada di DB
        response = self.client.get(reverse('explore_gunung:show_gunung', args=[fake_uuid]))
        self.assertEqual(response.status_code, 404)