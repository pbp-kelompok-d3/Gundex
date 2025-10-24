from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from logpendakian.models import LogPendakian
from explore_gunung.models import Gunung

class LogPendakianTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user("u1", "u1@example.com", "pass")
        cls.other = User.objects.create_user("u2", "u2@example.com", "pass")
        cls.g1 = Gunung.objects.create(nama="Kinabalu")
        cls.g2 = Gunung.objects.create(nama="Abang")

        cls.d1 = date.today()
        cls.d2 = cls.d1 + timedelta(days=3)

    # helpers
    def login(self, who=None):
        who = who or self.user
        self.client.login(username=who.username, password="pass")

    def ajax_get(self, url_name, *args):
        url = reverse(url_name, args=args)
        return self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def ajax_post(self, url_name, data, *args):
        url = reverse(url_name, args=args)
        return self.client.post(
            url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest", follow=True
        )

    # list
    def test_list_page_loads(self):
        self.login()
        r = self.client.get(reverse("logpendakian:list"))
        self.assertEqual(r.status_code, 200)

    # create
    def test_create_get_returns_form_json(self):
        self.login()
        r = self.ajax_get("logpendakian:create")
        self.assertEqual(r.status_code, 200)
        self.assertIn("html", r.json())

    def test_create_post_success(self):
        self.login()
        payload = {
            "gunung": self.g1.pk,
            "start_date": str(self.d1),
            "end_date": str(self.d2),
            "notes": "pertama",
            "summit_reached": "on",
        }
        r = self.ajax_post("logpendakian:create", payload)
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertTrue(j.get("ok"))
        self.assertIn("html", j)
        self.assertEqual(LogPendakian.objects.count(), 1)
        obj = LogPendakian.objects.first()
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.gunung, self.g1)
        self.assertEqual(obj.start_date, self.d1)

    def test_create_post_duplicate_unique_400(self):
        self.login()
        LogPendakian.objects.create(
            user=self.user, gunung=self.g1, start_date=self.d1, end_date=self.d2
        )
        r = self.ajax_post(
            "logpendakian:create",
            {"gunung": self.g1.pk, "start_date": str(self.d1), "end_date": str(self.d2)},
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("html", r.json())

    def test_create_post_missing_gunung_400(self):
        self.login()
        r = self.ajax_post(
            "logpendakian:create",
            {"start_date": str(self.d1), "end_date": str(self.d2)},
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("html", r.json())

    # update
    def test_update_get_returns_form_json(self):
        self.login()
        obj = LogPendakian.objects.create(
            user=self.user, gunung=self.g1, start_date=self.d1, end_date=self.d2
        )
        r = self.ajax_get("logpendakian:update", obj.pk)
        self.assertEqual(r.status_code, 200)
        self.assertIn("html", r.json())

    def test_update_post_success(self):
        self.login()
        obj = LogPendakian.objects.create(
            user=self.user,
            gunung=self.g1,
            start_date=self.d1,
            end_date=self.d2,
            notes="awal",
        )
        r = self.ajax_post(
            "logpendakian:update",
            {
                "gunung": self.g1.pk,
                "start_date": str(self.d1),
                "end_date": str(self.d2),
                "notes": "di-edit",
            },
            obj.pk,
        )
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertTrue(j.get("ok"))
        self.assertEqual(j.get("id"), str(obj.pk))
        obj.refresh_from_db()
        self.assertEqual(obj.notes, "di-edit")

    def test_update_permission_other_user_404(self):
        foreign = LogPendakian.objects.create(
            user=self.other, gunung=self.g1, start_date=self.d1, end_date=self.d2
        )
        self.login(self.user)
        r = self.ajax_get("logpendakian:update", foreign.pk)
        self.assertEqual(r.status_code, 404)

    # delete
    def test_delete_get_confirm_json(self):
        self.login()
        obj = LogPendakian.objects.create(
            user=self.user, gunung=self.g2, start_date=self.d1, end_date=self.d2
        )
        r = self.ajax_get("logpendakian:delete", obj.pk)
        self.assertEqual(r.status_code, 200)
        self.assertIn("html", r.json())

    def test_delete_post_success(self):
        self.login()
        obj = LogPendakian.objects.create(
            user=self.user, gunung=self.g2, start_date=self.d1, end_date=self.d2
        )
        r = self.client.post(
            reverse("logpendakian:delete", args=[obj.pk]),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(r.status_code, 200)
        j = r.json()
        self.assertTrue(j.get("ok"))
        self.assertEqual(j.get("id"), str(obj.pk))
        self.assertFalse(LogPendakian.objects.filter(pk=obj.pk).exists())

    def test_delete_permission_other_user_404(self):
        foreign = LogPendakian.objects.create(
            user=self.other, gunung=self.g2, start_date=self.d1, end_date=self.d2
        )
        self.login(self.user)
        r = self.ajax_get("logpendakian:delete", foreign.pk)
        self.assertEqual(r.status_code, 404)
