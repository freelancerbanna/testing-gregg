import datetime
from collections import OrderedDict

from django.conf import settings
from django.core.cache import caches
from django.utils.encoding import force_text
from rest_framework_extensions.key_constructor.bits import PaginationKeyBit, ListSqlQueryKeyBit, \
    RetrieveSqlQueryKeyBit, KeyBitBase, QueryParamsKeyBit
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor


def get_api_cache_key(model, slug_kwargs=None, instance=None):
    if slug_kwargs:
        slug_pairs = {
            key.replace('parent_lookup_', '').replace('__slug', '').split('__')[
                -1]: val
            for key, val in slug_kwargs.items()
            if 'slug' in key
            }
    elif instance:
        slug_pairs = {key: val.slug for key, val in instance.icmo_parents_dict.items()}
    else:
        raise ValueError("Must pass either slug_kwargs or instance")
    slug_pairs = OrderedDict(sorted(slug_pairs.items(), key=lambda t: t[0]))

    return 'api.%s.%s' % (
        model._meta.model_name,
        ".".join(["%s.%s" % (key, val) for key, val in slug_pairs.items()])
    )


# https://github.com/chibisov/drf-extensions/blob/master/docs/index.md
class UpdatedAtKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        key = get_api_cache_key(view_instance.get_queryset().model, kwargs)
        api_cache = caches[settings.API_KEY_CACHE_NAME]
        value = api_cache.get(key, None)
        if not value:
            value = datetime.datetime.utcnow()
            api_cache.set(key, value=value)
        return force_text(value)


class ICMOAPIListKeyConstructor(DefaultKeyConstructor):
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = UpdatedAtKeyBit()
    query_params = QueryParamsKeyBit()


class ICMOAPIRetrieveKeyConstructor(DefaultKeyConstructor):
    list_sql = RetrieveSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = UpdatedAtKeyBit()
