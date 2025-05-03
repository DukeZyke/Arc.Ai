from django.db import models

class Email(models.Model):
    sender_name = models.CharField(max_length=100)
    sender_icon = models.ImageField(upload_to='icons/')
    title = models.CharField(max_length=200)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title