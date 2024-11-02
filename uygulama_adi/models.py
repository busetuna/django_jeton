
from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

