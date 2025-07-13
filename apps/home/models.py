from django.db import models

from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False) 

    def __str__(self):
        return f"Notification pour {self.user.username} - {self.message[:20]}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
