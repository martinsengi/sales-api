import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=255)
    # depending on business case, it might be better to use category as a separate entity relation
    # for now we keep it as a charfield for more flexible user-definition
    # and use index for filtering
    category = models.CharField(_('category'), max_length=255, default='', blank=True)
    price = models.DecimalField(
        _('price'),
        default=0,
        max_digits=19,
        decimal_places=4,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['category']),
        ]

    def __str__(self) -> str:
        return self.name
