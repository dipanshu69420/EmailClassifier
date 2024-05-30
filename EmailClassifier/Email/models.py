from django.db import models

class Email(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    From = models.CharField(max_length=255)
    To = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    predicted_class = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='high')
    escalation=models.TextField()

    def __str__(self):
        return self.subject
