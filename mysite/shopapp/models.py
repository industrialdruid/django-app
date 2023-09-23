from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instanse: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instanse.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в интернет-магазине

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    #created_by = models.ForeignKey(User, on_delete=models.PROTECT, default=User.objects.filter(is_superuser=True)[0])
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, default=1)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to="")

    # @property
    # def description_short(self) -> str:
    #     if len(self.description) < 48:
    #         return self.description
    #     return self.description[:48] + '...'

    def __str__(self) -> str:
        return f"Product(pk={self.pk}, name={self.name!r})"

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    description = models.CharField(max_length=200, null=False, blank=True)
    image = models.ImageField(upload_to=product_images_directory_path)


class Order(models.Model):
    class Meta:
        ordering = ["created_at", "user"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    reciept = models.FileField(null=True, blank=True, upload_to='orders/reciepts/')
