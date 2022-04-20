from rest_framework import serializers

from core.serializers import IcmoModelSerializerMixin, IcmoNestedItemMixin
from icmo_users.models import IcmoUser
from .models import Company, CompanyUser, CompanyUserGroup, CompanyUserInvitation


class CompanySerializer(IcmoModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['slug', 'name', 'fiscal_year_start', 'fiscal_year_start_full_name', 'url',
                  'logo', 'logo_thumbnail']
        read_only_fields = ('slug', 'url', 'fiscal_year_start_full_name', 'logo_thumbnail')

    def update(self, instance, validated_data):
        if instance not in self.context['request'].user.owned_companies:
            raise serializers.ValidationError("You do not have permission to edit this company.")
        return super(CompanySerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        if not self.context['request'].user.can_create_company:
            raise serializers.ValidationError("Cannot add any more companies")
        validated_data['account'] = self.context['request'].user.billingaccount
        return super(CompanySerializer, self).create(validated_data)


class CompanyUserGroupSerializer(IcmoModelSerializerMixin, IcmoNestedItemMixin,
                                 serializers.ModelSerializer):
    parent_class = Company

    class Meta:
        model = CompanyUserGroup
        fields = ['slug', 'name', 'company', 'company_name', 'editable',
                  'revenue_plans', 'program_mix', 'budgets', 'performance',
                  'resources', 'timeline', 'task_boards', 'dashboards', 'permissions',
                  'live_plan_only', 'permitted_segments_list', 'publish_plans', 'archive_plans',
                  'share', 'moderate_shares']
        read_only_fields = ['slug', 'company', 'company_name']

    company = serializers.CharField(read_only=True, source='company.slug')
    company_name = serializers.CharField(read_only=True, source='company.name')


class CompanyUserSerializer(IcmoModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = ['slug', 'user', 'user_name', 'user_email', 'company', 'company_name', 'group',
                  'group_name', 'title', 'owner', 'permitted_segments_list']
        read_only_fields = ['slug', 'user', 'owner', 'company', 'company_name', 'user_name',
                            'user_email', 'group_name']

    user = serializers.CharField(source='user.email')
    group = serializers.CharField(source='group.slug')
    company = serializers.CharField(required=False, read_only=True, source='company.slug')
    user_name = serializers.CharField(required=False, read_only=True, source='user.full_name')
    user_email = serializers.CharField(required=False, read_only=True, source='user.email')
    group_name = serializers.CharField(required=False, read_only=True, source='group.name')
    company_name = serializers.CharField(required=False, read_only=True, source='company.name')

    def validate(self, validated_data):
        validated_data['group'] = CompanyUserGroup.objects.get(
            slug=validated_data['group']['slug'])
        validated_data['company'] = Company.objects.get(
            slug=self.context['kwargs']['company__slug'])
        return validated_data

    def update(self, instance, validated_data):
        validated_data['user'] = IcmoUser.objects.get(email=validated_data['user']['email'])
        return super(CompanyUserSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        if CompanyUser.objects.filter(user__email=validated_data['user']['email'],
                                      company=validated_data['company']).count() != 0:
            raise serializers.ValidationError(
                "This user already has permissions for this company.")

        invite = CompanyUserInvitation(
            inviting_user=self.context['request'].user,
            company=validated_data['company'],
            target_email=validated_data['user']['email'],
        )
        invite.save(request=self.context['request'])
        validated_data['user'] = invite.user
        return super(CompanyUserSerializer, self).create(validated_data)
