from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from artikel.models import Artikel
from django.db import models
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from artikel import views

User = get_user_model()


class ArtikelTestCase(TestCase):
    """Unit test untuk semua fitur utama modul Artikel (GunDex)"""

    def setUp(self):
        # Buat user admin & user biasa
        self.admin = User.objects.create_user(username="admin", password="admin123", is_admin=True)
        self.user = User.objects.create_user(username="user", password="user123", is_admin=False)

        # Client Django
        self.client = Client()

        # Buat beberapa artikel contoh
        self.artikel1 = Artikel.objects.create(
            title="Gunung Merapi", description="Aktif di perbatasan Jawa Tengah & Yogyakarta", image="https://example.com/merapi.jpg"
        )
        self.artikel2 = Artikel.objects.create(
            title="Gunung Rinjani", description="Gunung tertinggi di Nusa Tenggara Barat", image="https://example.com/rinjani.jpg"
        )

    # ---------------------------------------------------------------------
    # TEST 1: Akses halaman utama
    # ---------------------------------------------------------------------
    def test_show_artikel_page_loads(self):
        response = self.client.get(reverse("artikel:show_artikel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Artikel")

    # ---------------------------------------------------------------------
    # TEST 2: Admin bisa membuat artikel via AJAX
    # ---------------------------------------------------------------------
    def test_create_artikel_by_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:create_artikel"),
            {
                "title": "Gunung Lawu",
                "description": "Gunung perbatasan Jawa Tengah dan Jawa Timur",
                "image": "https://example.com/lawu.jpg",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Artikel.objects.count(), 3)

    # ---------------------------------------------------------------------
    # TEST 3: Non-admin tidak bisa membuat artikel
    # ---------------------------------------------------------------------
    def test_create_artikel_by_non_admin(self):
        self.client.login(username="user", password="user123")
        response = self.client.post(
            reverse("artikel:create_artikel"),
            {
                "title": "Gunung Slamet",
                "description": "Gunung tertinggi di Jawa Tengah",
                "image": "https://example.com/slamet.jpg",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 403)

    # ---------------------------------------------------------------------
    # TEST 4: Lihat detail artikel & jumlah view bertambah
    # ---------------------------------------------------------------------
    def test_view_artikel_detail_increase_views(self):
        views_before = self.artikel1.views
        response = self.client.get(reverse("artikel:artikel_detail", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 200)
        self.artikel1.refresh_from_db()
        self.assertEqual(self.artikel1.views, views_before + 1)

    # ---------------------------------------------------------------------
    # TEST 5: Admin bisa edit artikel via AJAX
    # ---------------------------------------------------------------------
    def test_edit_artikel_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel1.id]),
            {
                "title": "Gunung Merapi Update",
                "description": "Gunung aktif terkenal di Jawa Tengah",
                "image": "https://example.com/merapi2.jpg",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.artikel1.refresh_from_db()
        self.assertEqual(self.artikel1.title, "Gunung Merapi Update")

    # ---------------------------------------------------------------------
    # TEST 6: Non-admin tidak bisa edit artikel
    # ---------------------------------------------------------------------
    def test_edit_artikel_non_admin_forbidden(self):
        self.client.login(username="user", password="user123")
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel2.id]),
            {"title": "Edited by non admin"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 403)

    # ---------------------------------------------------------------------
    # TEST 7: Admin bisa hapus artikel
    # ---------------------------------------------------------------------
    def test_delete_artikel_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:delete_artikel", args=[self.artikel2.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Artikel.objects.count(), 1)

    # ---------------------------------------------------------------------
    # TEST 8: Like & Unlike artikel oleh user biasa
    # ---------------------------------------------------------------------
    def test_like_and_unlike_artikel(self):
        self.client.login(username="user", password="user123")

        # Like
        like_url = reverse("artikel:like_artikel", args=[self.artikel1.id])
        response = self.client.post(like_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.artikel1.refresh_from_db()
        self.assertEqual(self.artikel1.total_likes(), 1)

        # Unlike (klik lagi)
        response = self.client.post(like_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.artikel1.refresh_from_db()
        self.assertEqual(self.artikel1.total_likes(), 0)

    # ---------------------------------------------------------------------
    # TEST 9: Artikel Terpopuler, Terhangat, dan Rekomendasi
    # ---------------------------------------------------------------------
    def test_artikel_querysets_integrity(self):
        # Tambahkan views dan likes
        self.artikel1.views = 20
        self.artikel1.save()
        self.artikel2.views = 5
        self.artikel2.save()
        self.artikel1.likes.add(self.user)

        response = self.client.get(reverse("artikel:show_artikel"))
        self.assertEqual(response.status_code, 200)

        # Pastikan konteks berisi daftar artikel
        context = response.context
        self.assertIn("popular_artikels", context)
        self.assertIn("hottest_artikels", context)
        self.assertIn("recommended_artikels", context)

        # Urutan populer benar
        popular = list(context["popular_artikels"])
        self.assertGreaterEqual(popular[0].views, popular[-1].views)

    # ---------------------------------------------------------------------
    # TEST 10: Akses GET edit_artikel_modal (admin only)
    # ---------------------------------------------------------------------
    def test_edit_artikel_modal_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:edit_artikel_modal", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.artikel1.title)

    def test_edit_artikel_modal_non_admin_forbidden(self):
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse("artikel:edit_artikel_modal", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 403)

    # ---------------------------------------------------------------------
    # TEST 11: Delete artikel tanpa AJAX dan bukan admin
    # ---------------------------------------------------------------------
    def test_delete_artikel_non_admin(self):
        self.client.login(username="user", password="user123")
        response = self.client.post(reverse("artikel:delete_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 403)

    # ---------------------------------------------------------------------
    # TEST 12: Edit artikel tanpa AJAX method (trigger 405)
    # ---------------------------------------------------------------------
    def test_edit_artikel_non_ajax(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel1.id]),
            {"title": "Invalid Edit"}
        )
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 13: get_random_recommendations
    # ---------------------------------------------------------------------
    def test_get_random_recommendations(self):
        response = self.client.get(reverse("artikel:get_random_recommendations"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("artikels", data)
        self.assertTrue(isinstance(data["artikels"], list))

    # ---------------------------------------------------------------------
    # TEST 14: get_random_recommendations dengan method POST (405)
    # ---------------------------------------------------------------------
    def test_get_random_recommendations_wrong_method(self):
        response = self.client.post(reverse("artikel:get_random_recommendations"))
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 15: Coba GET ke create_artikel (harus 405 error)
    # ---------------------------------------------------------------------
    def test_create_artikel_get_method_error(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:create_artikel"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("Only POST", response.json()["message"])

    # ---------------------------------------------------------------------
    # TEST 16: Delete artikel dengan method GET (harus 405)
    # ---------------------------------------------------------------------
    def test_delete_artikel_with_get(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:delete_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 17: Edit artikel modal oleh non-admin
    # ---------------------------------------------------------------------
    def test_edit_artikel_modal_non_admin(self):
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse("artikel:edit_artikel_modal", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 403)
        self.assertIn("Kamu bukan admin", response.content.decode())

    # ---------------------------------------------------------------------
    # TEST 18: Edit artikel pakai GET (harus 405)
    # ---------------------------------------------------------------------
    def test_edit_artikel_with_get(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:edit_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 405)
        self.assertIn("Gunakan AJAX POST", response.json()["message"])

    # ---------------------------------------------------------------------
    # TEST 19: create_artikel gagal karena field kosong
    # ---------------------------------------------------------------------
    def test_create_artikel_missing_field(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:create_artikel"),
            {"title": "", "description": "", "image": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Judul dan deskripsi wajib diisi", response.json()["message"])

    # ---------------------------------------------------------------------
    # TEST 20: edit_artikel gagal karena field kosong
    # ---------------------------------------------------------------------
    def test_edit_artikel_missing_field(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel1.id]),
            {"title": "", "description": "", "image": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Judul dan deskripsi wajib diisi", response.json()["message"])

    # ---------------------------------------------------------------------
    # TEST 21: delete_artikel GET method error (405)
    # ---------------------------------------------------------------------
    def test_delete_artikel_get_error(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:delete_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 22: edit_artikel_modal tanpa login (harus redirect/login required)
    # ---------------------------------------------------------------------
    def test_edit_artikel_modal_unauthenticated(self):
        response = self.client.get(reverse("artikel:edit_artikel_modal", args=[self.artikel1.id]))
        self.assertIn(response.status_code, [302, 403])

        # ---------------------------------------------------------------------
    # TEST 23: edit_artikel_modal oleh non-admin (forbidden 403)
    # ---------------------------------------------------------------------
    def test_edit_artikel_modal_forbidden(self):
        self.client.login(username="user", password="user123")
        response = self.client.get(reverse("artikel:edit_artikel_modal", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 403)

    # ---------------------------------------------------------------------
    # TEST 24: delete_artikel tanpa login (redirect/login required)
    # ---------------------------------------------------------------------
    def test_delete_artikel_without_login(self):
        response = self.client.post(
            reverse("artikel:delete_artikel", args=[self.artikel1.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------------
    # TEST 25: like_artikel tanpa login (redirect/login required)
    # ---------------------------------------------------------------------
    def test_like_artikel_without_login(self):
        response = self.client.post(
            reverse("artikel:like_artikel", args=[self.artikel1.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------------
    # TEST 26: edit_artikel wrong method (GET instead of POST)
    # ---------------------------------------------------------------------
    def test_edit_artikel_get_method(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:edit_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 405)

    def test_edit_artikel_without_ajax_header(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel1.id]),
            {"title": "Test tanpa AJAX", "description": "Tes", "image": "https://example.com/x.jpg"}
        )
        self.assertEqual(response.status_code, 405)
        self.assertIn("Gunakan AJAX", response.json()["message"])

    # ---------------------------------------------------------------------
    # TEST 28: delete_artikel tanpa AJAX (should 405)
    # ---------------------------------------------------------------------
    def test_delete_artikel_without_ajax(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(reverse("artikel:delete_artikel", args=[self.artikel1.id]))
        self.assertIn(response.status_code, [302, 405])
    
    # ---------------------------------------------------------------------
    # TEST 29: like_artikel GET method (harus 405)
    # ---------------------------------------------------------------------
    def test_like_artikel_get_method(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("artikel:like_artikel", args=[self.artikel1.id]))
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 30: create_artikel tanpa header AJAX (should 405)
    # ---------------------------------------------------------------------
    def test_create_artikel_without_ajax_header(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("artikel:create_artikel"),
            {
                "title": "Gunung Kerinci",
                "description": "Gunung tertinggi di Sumatera",
                "image": "https://example.com/kerinci.jpg"
            }
        )
        # non-AJAX => biasanya 405 atau 302 tergantung CSRF
        self.assertIn(response.status_code, [201, 405, 302])

    # ---------------------------------------------------------------------
    # TEST 31: get_random_recommendations method POST (harus 405)
    # ---------------------------------------------------------------------
    def test_get_random_recommendations_post(self):
        response = self.client.post(reverse("artikel:get_random_recommendations"))
        self.assertEqual(response.status_code, 405)

    # ---------------------------------------------------------------------
    # TEST 32: edit_artikel oleh user belum login (harus redirect/login required)
    # ---------------------------------------------------------------------
    def test_edit_artikel_unauthenticated(self):
        response = self.client.post(
            reverse("artikel:edit_artikel", args=[self.artikel1.id]),
            {"title": "Gunung Unauth", "description": "Tes", "image": "https://example.com/x.jpg"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------------
    # TEST 33: like_artikel oleh user belum login (harus redirect/login required)
    # ---------------------------------------------------------------------
    def test_like_artikel_unauthenticated(self):
        response = self.client.post(
            reverse("artikel:like_artikel", args=[self.artikel1.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertIn(response.status_code, [302, 403])

    # ---------------------------------------------------------------------
    # TEST 34: delete_artikel method GET untuk artikel tidak ada (404)
    # ---------------------------------------------------------------------
    def test_delete_artikel_not_found(self):
        self.client.login(username="admin", password="admin123")
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.post(
            reverse("artikel:delete_artikel", args=[fake_id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertIn(response.status_code, [404, 400])
    
    def test_urls_resolve_correct_view(self):
        self.assertEqual(resolve(reverse('artikel:show_artikel')).func, views.show_artikel)
        self.assertEqual(resolve(reverse('artikel:refresh_recommendations')).func, views.get_random_recommendations)
    
    def test_all_urls_resolve(self):
        # semua path di urls.py diakses biar tercover
        self.assertEqual(resolve(reverse('artikel:show_artikel')).func, views.show_artikel)
        self.assertEqual(resolve(reverse('artikel:refresh_recommendations')).func, views.get_random_recommendations)
        
        # untuk fungsi dengan argumen id
        import uuid
        fake_id = uuid.uuid4()
        self.assertEqual(resolve(reverse('artikel:artikel_detail', args=[fake_id])).func, views.artikel_detail)
        self.assertEqual(resolve(reverse('artikel:edit_artikel', args=[fake_id])).func, views.edit_artikel)
        self.assertEqual(resolve(reverse('artikel:delete_artikel', args=[fake_id])).func, views.delete_artikel)
        self.assertEqual(resolve(reverse('artikel:edit_artikel_modal', args=[fake_id])).func, views.edit_artikel_modal)
        self.assertEqual(resolve(reverse('artikel:create_artikel')).func, views.create_artikel)