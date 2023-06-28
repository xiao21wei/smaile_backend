from rest_framework import serializers

from space.models import Rent
from user.models import User


class WorkerSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'identity', 'is_delete',
                  'company_name', 'contact_person', 'contact_phone', 'password',
                  'is_working', 'job_category']


class UserSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'identity', 'is_delete',
                  'company_name', 'legal_entity_name', 'contact_person', 'contact_phone',
                  'is_working', 'job_category']
