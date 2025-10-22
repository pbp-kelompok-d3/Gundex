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
    )
    mountain_name = models.CharField(max_length=200, db_index=True)
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
            models.Index(fields=["mountain_name"]),
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
                fields=["user", "mountain_name", "start_date"],
                name="uniq_user_mountain_start",
            ),
        ]

    def __str__(self):
        end = self.end_date or "ongoing"
        return f"{self.user} — {self.mountain_name} ({self.start_date}→{end})"

    @property
    def duration_days(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
