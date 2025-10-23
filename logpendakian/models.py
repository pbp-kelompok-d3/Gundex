import uuid
from django.db import models
from django.conf import settings
from django.db.models import Q, F

class LogPendakian(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="logs_pendakian",
        null=True, blank=True,
    )  
    gunung = models.ForeignKey(
        "explore_gunung.Gunung",
        on_delete=models.PROTECT,
        related_name="logs",
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    summit_reached = models.BooleanField(default=True)
    team_size = models.PositiveSmallIntegerField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "start_date"]),
            models.Index(fields=["gunung"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(end_date__gte=F("start_date")) | Q(end_date__isnull=True),
                name="end_gte_start_or_null",
            ),
            models.CheckConstraint(
                check=Q(rating__gte=1, rating__lte=5) | Q(rating__isnull=True),
                name="rating_1_5_or_null",
            ),
            models.UniqueConstraint(
                fields=["user", "gunung", "start_date"],
                name="uniq_user_gunung_start",
            ),
        ]

    def __str__(self):
        gunung_name = getattr(self.gunung, "nama", "(tanpa nama)")
        prof = getattr(self, "user", None)  # ini UserProfile
        if prof and getattr(prof, "display_name", None):
            user_name = prof.display_name
        elif prof and getattr(prof, "user", None):
            u = prof.user
            user_name = (getattr(u, "get_full_name", lambda: "")() or getattr(u, "username", "(anonim)"))
        else:
            user_name = "(anonim)"
        return f"{user_name} mendaki {gunung_name}"

    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    
