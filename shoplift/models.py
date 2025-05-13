from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image_url = models.URLField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    description = models.TextField(blank=True)
    available_sizes = models.CharField(max_length=100, help_text="Comma-separated sizes, e.g. S, M, L")
    available_colors = models.CharField(max_length=200, help_text="Comma-separated colors, e.g. Black, Red, Blue")

    def __str__(self):
        return self.name