# coding=utf-8
import re
from copy import copy
from decimal import Decimal

from django.conf import settings
from djmoney.models import fields as djmoney_fields
from rest_framework import serializers
from rest_framework.fields import Field, FloatField
from rest_framework.utils import html

from companies.models import Company
from core.helpers import get_currency_whole_number_display
from icmo_users.serializers import IcmoUserSerializer
from leads.models import Program
from revenues.models import RevenuePlan, Segment


class PercentField(FloatField):
    def to_internal_value(self, data):
        data = super(PercentField, self).to_internal_value(data)
        return int(data * 100)

    def to_representation(self, value):
        # convert integer to decimal
        return Decimal(value) / 100


class MoneyField(Field):
    initial = {}
    char_field = None
    decimal_field = None
    default_error_messages = dict(invalid_dict="Could not find the amount in this currency unit.")

    def __init__(self, max_digits=None, decimal_places=2, min_value=None, max_value=None, *args,
                 **kwargs):
        self.char_field = serializers.CharField()
        self.decimal_field = serializers.DecimalField(max_digits=max_digits,
                                                      decimal_places=decimal_places,
                                                      max_value=max_value, min_value=min_value)

        super(MoneyField, self).__init__(*args, **kwargs)
        self.char_field.bind(field_name='', parent=self)
        self.decimal_field.bind(field_name='', parent=self)

    def get_value(self, dictionary):
        # We override the default field access in order to support
        # dictionaries in HTML forms.
        if html.is_html_input(dictionary):
            ret = {}
            regex = re.compile(r'^%s\[([^\]]+)\]$' % re.escape(self.field_name))
            for field, value in dictionary.items():
                match = regex.match(field)
                if not match:
                    continue
                key = match.groups()[0]
                ret[key] = value
            if not ret:
                ret = html.parse_html_dict(dictionary, self.field_name)
            return ret

        return dictionary.get(self.field_name)

    def to_internal_value(self, data):
        """
        Validate that the input is a decimal number and return a Decimal
        instance.
        """
        currency = settings.ICMO_DEFAULT_CURRENCY
        amount = Decimal('0')
        if isinstance(data, basestring):
            amount = data
        elif isinstance(data, dict):
            if 'amount' not in data.keys():
                self.fail('invalid_dict')
            amount = data['amount']
            if 'currency' in data.keys():
                currency = self.char_field.run_validation(data['currency'])

        amount = self.decimal_field.run_validation(amount)
        return amount, currency

    def to_representation(self, value):
        localized_whole_number = get_currency_whole_number_display(value)
        return dict([
            ('amount', self.decimal_field.to_representation(value.amount)),
            ('currency', self.char_field.to_representation(value.currency.code)),
            ('localized', self.char_field.to_representation(str(value))),
            ('localized_whole_number', self.char_field.to_representation(localized_whole_number)),
        ])


class MoneyAmountReadOnlyField(MoneyField):
    def to_representation(self, value):
        return self.decimal_field.to_representation(value.amount)


class MoneyModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(MoneyModelSerializer, self).__init__(*args, **kwargs)
        self.serializer_field_mapping[djmoney_fields.MoneyField] = MoneyField


class MoneyModelAmountReadOnlySerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(MoneyModelAmountReadOnlySerializer, self).__init__(*args, **kwargs)
        self.serializer_field_mapping[djmoney_fields.MoneyField] = MoneyAmountReadOnlyField


class ModifiedByMixin(object):
    modified_by = IcmoUserSerializer(read_only=True)
    modified_by_name = serializers.CharField(read_only=True, source='modified_by.get_full_name')

    def update(self, instance, validated_data):
        instance.modified_by = self.context['request'].user
        return super(ModifiedByMixin, self).update(instance, validated_data)


def get_validated_data_object_or_none(validated_data, field, target_field, model, **kwargs):
    if field in validated_data:
        if validated_data[field][target_field]:
            kwargs[target_field] = validated_data[field][target_field]
            validated_data[field] = model.objects.get(**kwargs)
        else:
            validated_data[field] = None
    return validated_data


class IcmoNestedItemMixin(object):
    """
    Adds the objects relating to the path to the serializer
    """
    parent_class = None
    company = None
    revenue_plan = None
    segment = None
    program = None

    def get_fields(self):
        # todo, rewrite using levels?
        fields = super(IcmoNestedItemMixin, self).get_fields()
        if self.parent_class in (Company, RevenuePlan, Segment, Program):
            fields['company'] = serializers.CharField(read_only=True, required=False,
                                                      source='company.slug')
            fields['company_name'] = serializers.CharField(read_only=True, required=False,
                                                           source='company.slug')
        if self.parent_class in (RevenuePlan, Segment, Program):
            fields['revenue_plan'] = serializers.CharField(read_only=True, required=False,
                                                           source='revenue_plan.slug')
            fields['revenue_plan_name'] = serializers.CharField(read_only=True, required=False,
                                                                source='revenue_plan.name')

        if self.parent_class in (Segment, Program):
            fields['segment'] = serializers.CharField(read_only=True, required=False,
                                                      source='segment.slug')
            fields['segment_name'] = serializers.CharField(read_only=True, required=False,
                                                           source='segment.name')

        if self.parent_class in (Program,):
            fields['program'] = serializers.CharField(read_only=True, required=False,
                                                      source='program.slug')
            fields['program_name'] = serializers.CharField(read_only=True, required=False,
                                                           source='program.name')
        return fields

    def validate(self, validated_data):
        validated_data = super(IcmoNestedItemMixin, self).validate(validated_data)
        kwargs = self.context['kwargs']
        if self.parent_class in (Company, RevenuePlan, Segment):
            validated_data['company'] = Company.objects.get(slug=kwargs['company__slug'])

        if self.parent_class in (RevenuePlan, Segment, Program):
            validated_data['revenue_plan'] = RevenuePlan.objects.get(
                    company__slug=kwargs['company__slug'],
                    slug=kwargs['revenue_plan__slug']
            )

        if self.parent_class in (Segment, Program):
            validated_data['segment'] = Segment.objects.get(
                    company__slug=kwargs['company__slug'],
                    revenue_plan__slug=kwargs['revenue_plan__slug'],
                    slug=kwargs['segment__slug']
            )
        if self.parent_class in (Program,):
            validated_data['program'] = Program.objects.get(
                    company__slug=kwargs['company__slug'],
                    revenue_plan__slug=kwargs['revenue_plan__slug'],
                    segment__slug=kwargs['segment__slug'],
                    slug=kwargs['program__slug']
            )
        return validated_data


class IcmoModelSerializerMixin(object):
    def get_fields(self):
        fields = super(IcmoModelSerializerMixin, self).get_fields()
        fields['created'] = serializers.DateTimeField(read_only=True)
        fields['modified'] = serializers.DateTimeField(read_only=True)
        fields['modified_by'] = IcmoUserSerializer(read_only=True)
        fields['modified_by_name'] = serializers.CharField(read_only=True,
                                                           source='modified_by.get_full_name')
        return fields

    def update(self, instance, validated_data):
        instance.modified_by = self.context['request'].user
        return super(IcmoModelSerializerMixin, self).update(instance, validated_data)


class MPTTOrderedObjectSerializerMixin(object):
    slug_unique_with = None

    def get_fields(self):
        fields = super(MPTTOrderedObjectSerializerMixin, self).get_fields()
        fields['parent'] = serializers.CharField(read_only=False, required=False, allow_null=True,
                                                 allow_blank=True,
                                                 source='parent.slug')
        fields['reorder_target'] = serializers.CharField(read_only=False, required=False,
                                                         allow_blank=True,
                                                         allow_null=True)

        fields['order'] = serializers.CharField(read_only=True, required=False, allow_null=True)
        fields['original_order'] = serializers.CharField(read_only=True, required=False,
                                                         allow_null=True, source='order')
        fields['original_parent'] = serializers.CharField(read_only=True, required=False,
                                                          allow_null=True,
                                                          source='parent.slug')
        return fields

    def validate(self, validated_data):
        validated_data = super(MPTTOrderedObjectSerializerMixin, self).validate(validated_data)
        if validated_data.get('parent') and validated_data['parent'].get('slug'):
            kwargs = copy(self.context['kwargs'])
            kwargs['slug'] = validated_data['parent'].get('slug')
            validated_data['parent'] = self.Meta.model.objects.get(**kwargs)
        else:
            validated_data['parent'] = None
        return validated_data

    def update(self, instance, validated_data):
        item = super(MPTTOrderedObjectSerializerMixin, self).update(instance, validated_data)
        # If the item has been moved, move it above the reorder_target
        if validated_data.get('reorder_target'):
            kwargs = self.context['kwargs']
            kwargs['slug'] = validated_data['reorder_target']
            item.above(self.Meta.model.objects.get(**kwargs))
        return item

    def create(self, validated_data):
        validated_data = self.validate(validated_data)
        validated_data.pop('reorder_target')
        return super(MPTTOrderedObjectSerializerMixin, self).create(validated_data)
