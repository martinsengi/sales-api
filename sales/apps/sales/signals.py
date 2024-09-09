from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import SalesRecord


@receiver(post_save, sender=SalesRecord)
@receiver(post_delete, sender=SalesRecord)
def invalidate_salesrecord_api_cache(sender, instance, **kwargs):
    try:
        cache.delete_pattern('*api_salesrecord_list*')
        cache.delete_pattern('*api_salesdataaggregate_list*')
    except Exception as e:
        print(f'Failed to invalidate SalesRecord API cache: {e}')
