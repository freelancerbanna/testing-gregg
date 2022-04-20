from importlib import import_module

from django.conf import settings

from .notifications import BaseNotification


def get_notification_types():
    _notification_types = dict()
    for notification_type in settings.NOTIFICATION_TYPES:
        module_name, class_name = notification_type.rsplit('.', 1)
        module = import_module(module_name)
        klass = getattr(module, class_name)
        if issubclass(klass, BaseNotification):
            _notification_types[klass.slug] = klass
        else:
            raise ValueError("%s is not a sublcass of Notification" % klass)
    return _notification_types


NOTIFICATION_TYPES = get_notification_types()

NOTIFICATION_TYPE_CHOICES = [(item.slug, item.name) for item in NOTIFICATION_TYPES.values()]