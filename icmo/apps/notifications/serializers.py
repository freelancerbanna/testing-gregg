from rest_framework import serializers

from companies.models import Company, CompanyUser
from core.serializers import IcmoModelSerializerMixin, IcmoNestedItemMixin
from .models import CompanyUserNotificationSubscription


class CompanyUserNotificationSubscriptionSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin,
                                                    serializers.ModelSerializer):
    class Meta:
        model = CompanyUserNotificationSubscription
        fields = ['id', 'company_user', 'notification_type', 'frequency',
                  'notification_type_display']
        read_only_fields = ('company_user', 'company', 'notification_type_display')

    parent_class = Company
    notification_type_display = serializers.CharField(read_only=True,
                                                      source='get_notification_type_display')

    def validate(self, validated_data):
        validated_data = super(CompanyUserNotificationSubscriptionSerializer, self).validate(
            validated_data)
        validated_data['company_user'] = CompanyUser.objects.get(company=validated_data['company'],
                                                                 user=self.context['request'].user)
        if not validated_data.get('id') and CompanyUserNotificationSubscription.objects.filter(
                company=validated_data['company'],
                company_user=validated_data['company_user']).exists():
            raise serializers.ValidationError(
                'You are already subscribed to that type of notification.')
        return validated_data

    def create(self, validated_data):
        return super(CompanyUserNotificationSubscriptionSerializer, self).create(validated_data)
