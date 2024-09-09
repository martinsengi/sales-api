from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'name',
        'category',
        'get_price',
    )
    search_fields = (
        'uuid',
        'name',
        'category',
    )

    def get_price(self, obj: Product) -> str:
        return f'{obj.price:.2f}'

    get_price.short_description = _('price')
