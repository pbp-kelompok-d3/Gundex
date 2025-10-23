from django.test import TestCase, Client
from django.urls import reverse
from explore_gunung.models import Gunung
import uuid
from userprofile.models import UserProfile
from explore_gunung.forms import GunungForm
import json

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

        self.user = UserProfile.objects.create_user(
            username="tester", password="test123", email="test@example.com"
        )
        self.client.login(username="tester", password="test123")

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

class ExploreGunungExtraTests(TestCase):
    def setUp(self):
        self.client = Client()
        # bikin data Gunung baru khusus test ini
        self.gunung = Gunung.objects.create(
            nama="Gunung Test",
            ketinggian=1234,
            provinsi="Jawa Barat",
            foto="https://example.com/test.jpg",
            deksripsi="Gunung untuk testing"
        )
        # buat superuser dan login
        self.superuser = UserProfile.objects.create_superuser(
            username="admin", password="adminpass", email="admin@example.com"
        )
        self.client.login(username="admin", password="adminpass")

    def test_edit_gunung_get(self):
        """GET ke edit_gunung harus kembalikan form"""
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name=\"nama\"")

    def test_edit_gunung_post_valid_json(self):
        """POST JSON valid berhasil update"""
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {
            "nama": "Gunung Update",
            "provinsi": "Jawa Tengah",
            "ketinggian": 2000,
            "deskripsi": "Update test",
            "foto": "https://example.com/new.jpg"
        }
        response = self.client.post(
            url, data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.gunung.refresh_from_db()
        self.assertEqual(self.gunung.nama, "Gunung Update")

    def test_edit_gunung_post_invalid_json(self):
        """POST JSON rusak"""
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        response = self.client.post(
            url, data="{invalid_json", content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_edit_gunung_post_empty_fields(self):
        """POST dengan field kosong"""
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {"nama": "", "provinsi": ""}
        response = self.client.post(
            url, data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("tidak boleh kosong", response.json()['message'])

    def test_edit_gunung_post_exception(self):
        """Simulasi exception saat save"""
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {
            "nama": "Gunung Exception",
            "provinsi": "Bali"
        }
        # monkeypatch: buat method save raise error
        original_save = Gunung.save
        def broken_save(*args, **kwargs):
            raise Exception("DB error")
        Gunung.save = broken_save

        response = self.client.post(
            url, data=json.dumps(payload),
            content_type='application/json'
        )
        Gunung.save = original_save  # balikin method
        self.assertEqual(response.status_code, 500)
        self.assertIn("Gagal menyimpan", response.json()['message'])

    def test_get_gunung_json(self):
        url = reverse('explore_gunung:get_gunung_json', args=[self.gunung.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['nama'], self.gunung.nama)

    def test_delete_gunung(self):
        url = reverse('explore_gunung:delete_gunung', args=[self.gunung.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertFalse(Gunung.objects.filter(id=self.gunung.id).exists())

    def test_show_json_includes_superuser_flag(self):
        url = reverse('explore_gunung:show_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('is_superuser', data)
        self.assertTrue(data['is_superuser'])

    # ====== tests for GunungForm ======
    def test_gunung_form_valid(self):
        form_data = {
            'nama': 'Gunung Slamet',
            'ketinggian': 3428,
            'provinsi': 'Jawa Tengah',
            'foto': 'https://example.com/slamet.jpg',
            'deksripsi': 'Gunung tertinggi di Jawa Tengah'
        }
        form = GunungForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_gunung_form_invalid(self):
        form_data = {'nama': '', 'provinsi': ''}
        form = GunungForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_edit_gunung_post_valid_json(self):
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {
            "nama": "Gunung Update",
            "provinsi": "Jawa Tengah",
            "ketinggian": 2000,
            "deskripsi": "Update test",
            "foto": "https://example.com/new.jpg"
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_edit_gunung_post_invalid_json(self):
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        response = self.client.post(url, data="{invalid_json", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_edit_gunung_post_empty_fields(self):
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {"nama": "", "provinsi": ""}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("tidak boleh kosong", response.json()['message'])

    def test_edit_gunung_post_exception(self):
        url = reverse('explore_gunung:edit_gunung', args=[self.gunung.id])
        payload = {"nama": "Gunung Exception", "provinsi": "Bali"}
        original_save = Gunung.save
        Gunung.save = lambda *a, **kw: (_ for _ in ()).throw(Exception("DB error"))  # raise exception
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        Gunung.save = original_save
        self.assertEqual(response.status_code, 500)
        self.assertIn("Gagal menyimpan", response.json()['message'])

    def test_get_gunung_json(self):
        url = reverse('explore_gunung:get_gunung_json', args=[self.gunung.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['nama'], self.gunung.nama)

    def test_delete_gunung(self):
        url = reverse('explore_gunung:delete_gunung', args=[self.gunung.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Gunung.objects.filter(id=self.gunung.id).exists())

class GunungFormTests(TestCase):
    def test_clean_nama_removes_html(self):
        form = GunungForm(data={
            "nama": "<b>Gunung Merapi</b>",
            "ketinggian": 2930,
            "provinsi": "Yogyakarta",
            "foto": "https://example.com/merapi.jpg",
            "deksripsi": "Deskripsi gunung"
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["nama"], "Gunung Merapi")

    def test_clean_deksripsi_removes_html(self):
        form = GunungForm(data={
            "nama": "Gunung Merapi",
            "ketinggian": 2930,
            "provinsi": "Yogyakarta",
            "foto": "https://example.com/merapi.jpg",
            "deksripsi": "<p>Gunung aktif</p>"
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["deksripsi"], "Gunung aktif")

    def test_form_invalid_missing_required(self):
        form = GunungForm(data={
            "nama": "",
            "ketinggian": 2930,
            "provinsi": "",
            "foto": "https://example.com/merapi.jpg",
            "deksripsi": "Deskripsi"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("nama", form.errors)
        self.assertIn("provinsi", form.errors)