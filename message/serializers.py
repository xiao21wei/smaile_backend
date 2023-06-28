from rest_framework import serializers

from message.models import Message, AppointmentRecord
from user.models import User


class MessageSerialize(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class AppointmentSerialize(serializers.ModelSerializer):
    class Meta:
        model = AppointmentRecord
        fields = "__all__"
