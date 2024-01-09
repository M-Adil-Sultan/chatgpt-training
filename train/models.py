from django.db import models

# Create your models here.

class Train_dataset(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=1000)
    answers = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message