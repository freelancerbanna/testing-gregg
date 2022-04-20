from __future__ import print_function
from __future__ import print_function

import datetime

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from mptt.signals import node_moved

from core.api_cache import get_api_cache_key
from core.models import DenormalizedIcmoParentsMixin


@receiver(node_moved, dispatch_uid='post_move_handler')
def post_move_handler(sender, instance, target, *args, **kwargs):
    print('post move handler for %s' % instance)
    old_parent_id = instance.get_dirty_fields(True).get('parent')
    if old_parent_id:
        try:
            old_parent = instance.__class__.objects.get(id=old_parent_id)
            old_parent.save()
            print("resaving old parent: %s" % old_parent)
        except ObjectDoesNotExist:
            pass
    if target:
        print("resaving new parent: %s" % target)
        target.save()


@receiver([post_save, post_delete])
def change_api_updated_at(sender=None, instance=None, *args, **kwargs):
    if not issubclass(sender, DenormalizedIcmoParentsMixin):
        return
    api_cache = caches[settings.API_KEY_CACHE_NAME]
    api_cache.set(get_api_cache_key(sender, instance=instance), datetime.datetime.utcnow())
