from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from userprofile.models import UserProfile
from explore_gunung.models import Gunung
from wishlist.models import WishlistItem
import json
import uuid

User = get_user_model()


class WishlistViewsTestCase(TestCase):
    """Test case untuk semua views di wishlist app"""
    
    def setUp(self):
        """Setup data yang dibutuhkan untuk testing"""
        # Create test user
        self.client = Client()
        self.user = UserProfile.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create another user untuk test isolation
        self.other_user = UserProfile.objects.create_user(
            username='otheruser',
            password='otherpass123',
            email='other@example.com'
        )
        
        # Create test gunung
        self.gunung1 = Gunung.objects.create(
            nama='Gunung Semeru',
            ketinggian=3676,
            provinsi='Jawa Timur',
            foto='https://example.com/semeru.jpg',
            deksripsi='Gunung tertinggi di Pulau Jawa'
        )
        
        self.gunung2 = Gunung.objects.create(
            nama='Gunung Rinjani',
            ketinggian=3726,
            provinsi='Nusa Tenggara Barat',
            foto='https://example.com/rinjani.jpg',
            deksripsi='Gunung berapi aktif di Lombok'
        )
        
        # Create wishlist item untuk user
        self.wishlist_item = WishlistItem.objects.create(
            user=self.user,
            gunung=self.gunung1
        )
    
    def tearDown(self):
        """Clean up after each test"""
        WishlistItem.objects.all().delete()
        Gunung.objects.all().delete()
        UserProfile.objects.all().delete()


    # ===== TEST SHOW_WISHLIST VIEW =====
    
    def test_show_wishlist_not_authenticated(self):
        """Test akses wishlist tanpa login harus redirect ke login"""
        response = self.client.get(reverse('wishlist:show_wishlist'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn('/userprofile/login/', response.url)
    
    def test_show_wishlist_authenticated(self):
        """Test akses wishlist dengan login berhasil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist:show_wishlist'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')
        self.assertIn('items', response.context)
        self.assertEqual(response.context['nama_user'], 'testuser')
    
    def test_show_wishlist_only_user_items(self):
        """Test bahwa user hanya melihat wishlist miliknya sendiri"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist:show_wishlist'))
        
        items = response.context['items']
        self.assertEqual(items.count(), 1)
        self.assertEqual(items[0].gunung.nama, 'Gunung Semeru')
    
    def test_show_wishlist_empty_for_new_user(self):
        """Test wishlist kosong untuk user yang belum punya wishlist"""
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(reverse('wishlist:show_wishlist'))
        
        items = response.context['items']
        self.assertEqual(items.count(), 0)


    # ===== TEST GET_WISHLIST_JSON VIEW =====
    
    def test_get_wishlist_json_not_authenticated(self):
        """Test akses JSON endpoint tanpa login"""
        response = self.client.get(reverse('wishlist:get_wishlist_json'))
        self.assertEqual(response.status_code, 302)
    
    def test_get_wishlist_json_authenticated(self):
        """Test JSON endpoint mengembalikan data wishlist user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist:get_wishlist_json'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['gunung_nama'], 'Gunung Semeru')
        self.assertEqual(data[0]['gunung_id'], str(self.gunung1.id))
        self.assertIn('added_at', data[0])
    
    def test_get_wishlist_json_multiple_items(self):
        """Test JSON dengan multiple wishlist items"""
        WishlistItem.objects.create(user=self.user, gunung=self.gunung2)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist:get_wishlist_json'))
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
    
    def test_get_wishlist_json_user_isolation(self):
        """Test bahwa JSON hanya return wishlist user yang login"""
        WishlistItem.objects.create(user=self.other_user, gunung=self.gunung2)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('wishlist:get_wishlist_json'))
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)  # Hanya 1 item milik testuser


    # ===== TEST ADD_TO_WISHLIST_AJAX VIEW =====
    
    def test_add_to_wishlist_not_authenticated(self):
        """Test add wishlist tanpa login"""
        response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({'gunung_id': str(self.gunung2.id)}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
    
    def test_add_to_wishlist_success(self):
        """Test berhasil menambahkan gunung ke wishlist"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({'gunung_id': str(self.gunung2.id)}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertIn('Rinjani', data['message'])
        
        # Verify item created in database
        self.assertTrue(
            WishlistItem.objects.filter(
                user=self.user, 
                gunung=self.gunung2
            ).exists()
        )
    
    def test_add_to_wishlist_duplicate(self):
        """Test menambahkan gunung yang sudah ada di wishlist"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({'gunung_id': str(self.gunung1.id)}),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'exists')
        self.assertIn('sudah ada', data['message'].lower())
        
        # Verify tidak ada duplicate di database
        count = WishlistItem.objects.filter(
            user=self.user, 
            gunung=self.gunung1
        ).count()
        self.assertEqual(count, 1)
    
    def test_add_to_wishlist_invalid_gunung_id(self):
        """Test menambahkan dengan gunung_id yang tidak valid"""
        self.client.login(username='testuser', password='testpass123')
        
        fake_uuid = str(uuid.uuid4())
        response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({'gunung_id': fake_uuid}),
            content_type='application/json'
        )
        
        # Bisa return 404 atau 500 tergantung implementasi
        self.assertIn(response.status_code, [404, 500])
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
    
    def test_add_to_wishlist_missing_gunung_id(self):
        """Test request tanpa gunung_id"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Bisa return 404 atau 500 tergantung implementasi
        self.assertIn(response.status_code, [404, 500])
    
    def test_add_to_wishlist_get_method(self):
        """Test menggunakan GET method (harus gagal)"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('wishlist:add_to_wishlist_ajax'))
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'failed')


    # ===== TEST REMOVE_FROM_WISHLIST_AJAX VIEW =====
    
    def test_remove_from_wishlist_not_authenticated(self):
        """Test remove wishlist tanpa login"""
        response = self.client.post(
            reverse('wishlist:remove_from_wishlist_ajax', args=[self.wishlist_item.id])
        )
        self.assertEqual(response.status_code, 302)
    
    def test_remove_from_wishlist_success(self):
        """Test berhasil menghapus item dari wishlist"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:remove_from_wishlist_ajax', args=[self.wishlist_item.id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['status'], 'success')
        self.assertIn('Semeru', data['message'])
        
        # Verify item deleted from database
        self.assertFalse(
            WishlistItem.objects.filter(id=self.wishlist_item.id).exists()
        )
    
    def test_remove_from_wishlist_other_user_item(self):
        """Test user tidak bisa menghapus wishlist user lain"""
        other_item = WishlistItem.objects.create(
            user=self.other_user,
            gunung=self.gunung2
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:remove_from_wishlist_ajax', args=[other_item.id])
        )
        
        # Bisa return 404 atau 500 tergantung implementasi
        self.assertIn(response.status_code, [404, 500])
        
        # Verify item still exists
        self.assertTrue(
            WishlistItem.objects.filter(id=other_item.id).exists()
        )
    
    def test_remove_from_wishlist_invalid_id(self):
        """Test menghapus dengan ID yang tidak ada"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:remove_from_wishlist_ajax', args=[99999])
        )
        
        # Bisa return 404 atau 500 tergantung implementasi
        self.assertIn(response.status_code, [404, 500])
    
    def test_remove_from_wishlist_get_method(self):
        """Test menggunakan GET method (harus gagal)"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('wishlist:remove_from_wishlist_ajax', args=[self.wishlist_item.id])
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'failed')


    # ===== TEST MODEL CONSTRAINTS =====
    
    def test_wishlist_unique_constraint(self):
        """Test unique_together constraint pada model"""
        from django.db import IntegrityError
        
        # Gunakan transaction.atomic untuk handle IntegrityError
        from django.db import transaction
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WishlistItem.objects.create(
                    user=self.user,
                    gunung=self.gunung1  # Sudah ada di setUp
                )
    
    def test_wishlist_cascade_delete_user(self):
        """Test wishlist terhapus saat user dihapus"""
        test_user = UserProfile.objects.create_user(
            username='tempuser',
            password='temppass',
            email='temp@example.com'
        )
        temp_item = WishlistItem.objects.create(user=test_user, gunung=self.gunung2)
        temp_item_id = temp_item.id
        
        # Verify item created
        self.assertTrue(
            WishlistItem.objects.filter(id=temp_item_id).exists()
        )
        
        # Delete user
        test_user.delete()
        
        # Verify wishlist item also deleted (cascade)
        self.assertFalse(
            WishlistItem.objects.filter(id=temp_item_id).exists()
        )
    
    def test_wishlist_cascade_delete_gunung(self):
        """Test wishlist terhapus saat gunung dihapus"""
        test_gunung = Gunung.objects.create(
            nama='Gunung Test',
            ketinggian=2000,
            provinsi='Test Province',
            deksripsi='Test mountain'
        )
        temp_item = WishlistItem.objects.create(user=self.user, gunung=test_gunung)
        temp_item_id = temp_item.id
        
        # Verify item created
        self.assertTrue(
            WishlistItem.objects.filter(id=temp_item_id).exists()
        )
        
        # Delete gunung
        test_gunung.delete()
        
        # Verify wishlist item also deleted (cascade)
        self.assertFalse(
            WishlistItem.objects.filter(id=temp_item_id).exists()
        )


class WishlistIntegrationTestCase(TestCase):
    """Integration tests untuk workflow lengkap wishlist"""
    
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create_user(
            username='integrationuser',
            password='integrationpass',
            email='integration@example.com'
        )
        
        self.gunung = Gunung.objects.create(
            nama='Gunung Integration',
            ketinggian=3000,
            provinsi='Integration Province',
            deksripsi='Integration test mountain'
        )
    
    def test_complete_wishlist_workflow(self):
        """Test complete user workflow: add -> view -> remove"""
        # 1. Login
        login_success = self.client.login(
            username='integrationuser', 
            password='integrationpass'
        )
        self.assertTrue(login_success)
        
        # 2. Add to wishlist
        add_response = self.client.post(
            reverse('wishlist:add_to_wishlist_ajax'),
            data=json.dumps({'gunung_id': str(self.gunung.id)}),
            content_type='application/json'
        )
        self.assertEqual(add_response.status_code, 200)
        
        # 3. Check JSON endpoint
        json_response = self.client.get(reverse('wishlist:get_wishlist_json'))
        data = json.loads(json_response.content)
        self.assertEqual(len(data), 1)
        
        # 4. Check HTML page
        html_response = self.client.get(reverse('wishlist:show_wishlist'))
        self.assertEqual(html_response.status_code, 200)
        self.assertEqual(html_response.context['items'].count(), 1)
        
        # 5. Remove from wishlist
        item_id = data[0]['id']
        remove_response = self.client.post(
            reverse('wishlist:remove_from_wishlist_ajax', args=[item_id])
        )
        self.assertEqual(remove_response.status_code, 200)
        
        # 6. Verify empty
        final_json = self.client.get(reverse('wishlist:get_wishlist_json'))
        final_data = json.loads(final_json.content)
        self.assertEqual(len(final_data), 0)