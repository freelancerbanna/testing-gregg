from rest_framework import serializers
from rest_framework_extensions.serializers import PartialUpdateSerializerMixin

from companies.models import Company
from core.serializers import MoneyModelSerializer, ModifiedByMixin, IcmoModelSerializerMixin
from icmo_users.serializers import IcmoUserSerializer
from .models import RevenuePlan, Segment


class RevenuePlanSerializer(ModifiedByMixin, PartialUpdateSerializerMixin,
                            serializers.ModelSerializer):
    class Meta:
        model = RevenuePlan
        fields = (
            'slug', 'company',
            'name', 'plan_type', 'plan_year', 'url',
            # Computed
            'owner', 'owner_name',
            'created', 'modified', 'modified_by', 'modified_by_name',
        )
        read_only_fields = (
            'slug', 'company',
            # Computed
            'owner', 'owner_name', 'url',
            'created', 'modified', 'modified_by', 'modified_by_name',
        )

    owner = IcmoUserSerializer(read_only=True)
    company = serializers.CharField(read_only=True, source='company.slug')
    owner_name = serializers.CharField(read_only=True, source='owner.get_full_name')

    modified_by = IcmoUserSerializer(read_only=True)
    modified_by_name = serializers.CharField(read_only=True, source='modified_by.get_full_name')

    def update(self, instance, validated_data):
        instance.modified_by = self.context['request'].user
        return super(RevenuePlanSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['owner'] = request.user
        return super(RevenuePlanSerializer, self).create(validated_data)

    def validate(self, data):
        kwargs = self.context['kwargs']
        data['company'] = Company.objects.get(slug=kwargs['company__slug'])

        existing_plan = RevenuePlan.objects.filter(company=data['company'],
                                                   name=data['name'])
        if self.instance:
            existing_plan = existing_plan.exclude(pk=self.instance.pk)

        if existing_plan.exists():
            raise serializers.ValidationError(
                "<b>A revenue plan named <i>%s</i> already exists</b><br>"
                "Revenue Plan names must be unique across the company including published, "
                "draft, archive, and plans in the recycle bin. We suggest including the year, ex: "
                "Revenue Plan 2016." % data['name']
            )
        return data


class SegmentSerializer(IcmoModelSerializerMixin, MoneyModelSerializer):
    class Meta:
        model = Segment
        fields = [
            'slug', 'revenue_plan', 'company',
            'name',
            'goal_q1', 'goal_q2', 'goal_q3', 'goal_q4', 'average_sale',
            # cached
            'goal_annual',
            
            # previous
            'prev_q1', 'prev_q2', 'prev_q3', 'prev_q4', 'prev_average_sale',
            # cached
            'prev_annual',
        ]
        read_only_fields = [
            'slug', 'revenue_plan', 'company',
            # cached
            'goal_annual', 'prev_annual',
        ]

    revenue_plan = serializers.CharField(read_only=True, source='revenue_plan.slug')
    company = serializers.CharField(read_only=True, source='company.slug')

    def create(self, validated_data):
        kwargs = self.context['kwargs']
        validated_data['revenue_plan'] = RevenuePlan.objects.get(
            company__slug=kwargs['company__slug'], slug=kwargs['revenue_plan__slug'])
        return super(SegmentSerializer, self).create(validated_data)
