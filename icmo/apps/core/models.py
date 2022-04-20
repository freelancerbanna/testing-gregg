from collections import OrderedDict

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.db import transaction
from django.db.models import Manager
from django.dispatch import Signal
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from localflavor.ca.ca_provinces import PROVINCE_CHOICES
from localflavor.us.us_states import STATE_CHOICES
from mptt.managers import TreeManager

BLANK_CHOICE = (('', ''),)
STATE_AND_PROVINCE_CHOICES = tuple(STATE_CHOICES) + tuple(PROVINCE_CHOICES)
SORTED_STATE_AND_PROVINCE = tuple(sorted(STATE_AND_PROVINCE_CHOICES, key=lambda x: x[1]))
COUNTRY_CHOICES = (
    ('US', 'United States'),
    ('CA', 'Canada')
)

ICMO_LEVELS = OrderedDict()  # OrderedDict constructor does not preserve key order, thus:
ICMO_LEVELS['campaign'] = dict(parent='program', children=None)
ICMO_LEVELS['program'] = dict(parent='segment', children='campaign')
ICMO_LEVELS['custom_budget_line_item'] = dict(parent='segment', children=None)
ICMO_LEVELS['segment'] = dict(parent='revenue_plan',
                              children=['program', 'custom_budget_line_item'])
ICMO_LEVELS['revenue_plan'] = dict(parent='company', children='segment')
ICMO_LEVELS['company'] = dict(parent=None, children='revenue_plan')

# signals
icmo_object_activated = Signal(providing_args=['instance'])
icmo_object_deactivated = Signal(providing_args=['instance'])


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(is_active=True)


class ActiveParentsManager(models.Manager):
    def get_queryset(self):
        qs = super(ActiveParentsManager, self).get_queryset().filter(is_active=True)
        kwargs = dict()
        if hasattr(self.model, 'icmo_parent_levels'):
            if type(self.model.icmo_parent_levels) not in (list, tuple):
                raise ValueError(
                    "To use this manager you must explicitly set the icmo_parent_levels property "
                    "as a list or tuple")
            for parent in self.model.icmo_parent_levels:
                kwargs["%s__is_active" % parent] = True
            return qs.select_related(*self.model.icmo_parent_levels).filter(**kwargs)
        return qs.all()


class ActiveRelatedTreeManager(TreeManager, ActiveParentsManager):
    pass


class NoUpdatesModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Updates are disabled on objects of this model.")
        super(NoUpdatesModel, self).save(*args, **kwargs)


class PartialUpdatesModel(DirtyFieldsMixin, models.Model):
    updateable_fields = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields().keys()
        forbidden_changed_fields = set(dirty_fields) - set(self.updateable_fields or [])
        if self.pk and forbidden_changed_fields:
            raise ValueError(
                "Only some fields of this model can be changed after update. "
                "These fields were changed and should not be: %s" % forbidden_changed_fields)
        super(PartialUpdatesModel, self).save(*args, **kwargs)


class DeactivateableModel(models.Model):
    class Meta:
        abstract = True

    is_active = models.BooleanField(_('active'), default=True)

    def deactivate(self, user=None):
        self.is_active = False
        if user:
            self.modified_by = user
        self.save()
        icmo_object_deactivated.send(sender=self.__class__, instance=self)

    def activate(self, user=None):
        self.is_active = True
        if user:
            self.modified_by = user
        self.save()
        icmo_object_activated.send(sender=self.__class__, instance=self)

    objects = ActiveParentsManager()
    all_objects = Manager()


class IcmoModel(DirtyFieldsMixin, DeactivateableModel, TimeStampedModel):
    class Meta:
        abstract = True

    do_not_enqueue = False  # Prevents tasks for being enqueued in post_save handlers
    modified_by = models.ForeignKey('icmo_users.IcmoUser', related_name='%(class)s_last_modified',
                                    blank=True, null=True, editable=False)

    def __init__(self, *args, **kwargs):
        self.do_not_enqueue = transaction.get_connection().in_atomic_block
        if 'do_not_enqueue' in kwargs:
            self.do_not_enqueue = kwargs.pop('do_not_enqueue')
        super(IcmoModel, self).__init__(*args, **kwargs)

    @cached_property
    def unique_slug(self):
        if hasattr(self._meta, 'unique_together'):
            for uniques in self._meta.unique_together:
                if 'slug' in uniques:
                    return "%s/%s" % (
                        "/".join([getattr(self, x).slug for x in uniques if x != 'slug']),
                        self.slug)
        return self.slug

    @classmethod
    def get_by_unique_slug(cls, unique_slug):
        """
        Note that by design this will also return deactivated objects (using the all_objects
        manager)
        :param unique_slug:
        :return:
        """
        uniques = cls._get_unique_slug_fields()
        if '/' in unique_slug:
            other = [x for x in uniques if x != 'slug']
            uslug_bits = unique_slug.split('/')
            kwargs = {'slug': uslug_bits.pop()}
            for idx, field in enumerate(other):
                kwargs["%s__slug" % field] = uslug_bits[idx]
            return cls.all_objects.get(**kwargs)
        return cls.all_objects.get(slug=unique_slug)

    @classmethod
    def get_by_unique_slug_or_404(cls, unique_slug):
        try:
            return cls.get_by_unique_slug(unique_slug)
        except cls.DoesNotExist:
            raise Http404

    @classmethod
    def _get_unique_slug_fields(cls):
        if hasattr(cls._meta, 'unique_together'):
            for uniques in cls._meta.unique_together:
                if 'slug' in uniques:
                    return uniques
        return ['slug']

    def save(self, *args, **kwargs):
        # add a flag if this method is being called in a transaction
        # tasks cannot run immediately because they will be run outside of
        # this transaction.  Can be overriden with a kwarg.
        self.do_not_enqueue = transaction.get_connection().in_atomic_block
        if 'do_not_enqueue' in kwargs:
            self.do_not_enqueue = kwargs.pop('do_not_enqueue')
        super(IcmoModel, self).save(*args, **kwargs)


class DenormalizedIcmoParentsMixin(object):
    # If a model is not a level itself, but is attached to an level object,
    # then it will have a foreignkey to the model it is linked to, and that
    # key should not be considered its parent
    icmo_level = None
    is_attached = False

    @property
    def icmo_level(self):
        if self._meta.model_name in ICMO_LEVELS:
            return self._meta.model_name
        raise ValueError("Level could not be autoconfigured for model %s" % self._meta.model_name)

    @property
    def icmo_object(self):
        return getattr(self, self.icmo_level)

    @property
    def icmo_object_type(self):
        return self.icmo_level

    @property
    def icmo_parents(self):
        return [getattr(self, x) for x in self.icmo_parent_levels]

    @property
    def icmo_parents_dict(self):
        return {x: getattr(self, x) for x in self.icmo_parent_levels}

    @property
    def icmo_object_id(self):
        if self.is_attached:
            return getattr(self, "%s_id" % self.icmo_level)
        else:
            return self.pk

    @property
    def icmo_parent_levels(self):
        levels = []
        parent = self.icmo_level
        while parent is not None:
            parent = ICMO_LEVELS[parent]['parent']
            if parent:
                levels.append(parent)
        return levels

    @property
    def icmo_parent_level(self):
        return ICMO_LEVELS[self.icmo_level]['parent']

    @property
    def icmo_child_levels(self):
        children = ICMO_LEVELS[self.icmo_level]['children']
        if children and type(children) is not list:
            children = [children]
        return children

    @property
    def icmo_parent_id(self):
        if self.icmo_parent_level:
            return getattr(self, "%s_id" % self.icmo_parent_level)
        return None

    @property
    def icmo_parent(self):
        return getattr(self, self.icmo_parent_level)

    @property
    def icmo_parent_filter_kwargs(self):
        return {"%s_id" % self.icmo_parent_level: self.icmo_parent_id}

    def set_icmo_parents(self):
        for level in self.icmo_parent_levels:
            prop_name = "%s_id" % level
            # This should prevent extra db hits unless we really need them
            if (hasattr(self, prop_name) and
                    (not getattr(self, prop_name) or prop_name in self.get_dirty_fields()) and
                    hasattr(self.icmo_parent, prop_name)
                ):
                setattr(self, prop_name, getattr(self.icmo_parent, prop_name))

    def save(self, *args, **kwargs):
        self.set_icmo_parents()
        super(DenormalizedIcmoParentsMixin, self).save(*args, **kwargs)
