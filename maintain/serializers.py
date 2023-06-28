from rest_framework import serializers

from maintain.models import MaintenanceRecord
from message.models import Message
from user.models import User


class MaintainSerialize(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"
