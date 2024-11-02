from django.db import models
from uygulama_adi.models import Product as ProductA
from kbkmarket.models import Product2

class MatchProduct(models.Model):
    product_a_id = models.ForeignKey(ProductA, on_delete=models.CASCADE)
    product_b_id = models.ForeignKey(Product2, on_delete=models.CASCADE)
    similarity = models.IntegerField()

    class Meta:
        db_table = 'match_matchedproduct' 
        unique_together = ('product_a_id', 'product_b_id')

    def __str__(self):
        return f"{self.product_a_id.title} - {self.product_b_id.title} ({self.similarity}%)"
