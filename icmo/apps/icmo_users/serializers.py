from rest_framework import serializers

from icmo_users.models import IcmoUser


class IcmoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = IcmoUser
        fields = ['first_name', 'last_name', 'email', 'employer', 'full_name']
        read_only_fields = ['first_name', 'last_name', 'email', 'employer', 'full_name']

    full_name = serializers.CharField(read_only=True, source='get_full_name')
    employer = serializers.CharField(read_only=True, source='employer.slug')
