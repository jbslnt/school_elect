from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ElectionEvent(models.Model):
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def is_active(self):
        now_time = timezone.now()
        return self.start_time <= now_time <= self.end_time

    def status(self):
        """Returns a string status: Upcoming, Ongoing, or Ended."""
        now_time = timezone.now()
        if not self.start_time or not self.end_time:
            return "Not Scheduled"
        if now_time < self.start_time:
            return "Upcoming"
        elif now_time > self.end_time:
            return "Ended"
        return "Ongoing"

    status.short_description = 'Status'

    def has_ended(self):
        return timezone.now() > self.end_time

    def __str__(self):
        return self.title


class Position(models.Model):
    title = models.CharField(max_length=100)
    event = models.ForeignKey(ElectionEvent, on_delete=models.CASCADE, related_name='positions')

    def __str__(self):
        return f"{self.title} - {self.event}"


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    total_vote = models.IntegerField(default=0, editable=False)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Candidate Pic", upload_to='images/')
    description = models.TextField(blank=True, null=True)
    partylist = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.position.title}"


class UserVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'candidate')

    def __str__(self):
        return f"{self.user.username} voted for {self.candidate.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class ControlVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.position} - {self.status}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    program = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"
