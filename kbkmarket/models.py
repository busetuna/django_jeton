from django.db import models

class Product2(models.Model):
    title = models.CharField(max_length=255, unique=True)  # title alanını benzersiz yap
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    url = models.URLField(max_length=200)
    image_url = models.URLField(max_length=200, null=True)

    def __str__(self):
        return self.title
