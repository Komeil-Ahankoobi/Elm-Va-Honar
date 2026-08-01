from django.db import models

from accounts.validators import validate_iranian_cellphone_number

# Create your models here.
class NewsLetterModel(models.Model):
    phone_number = models.CharField(max_length=12, validators=[validate_iranian_cellphone_number])
    
    def __str__(self):
        return self.phone_number