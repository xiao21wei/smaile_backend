from django.db import models


# Create your models here.
class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, default="")
    description = models.CharField(max_length=256, null=True, default="")
    sender_id = models.IntegerField()
    sender_name = models.CharField(max_length=32, default="")
    recipient_id = models.IntegerField()
    status = models.CharField(max_length=32, default="unread")


class AppointmentRecord(models.Model):
    appointment_record_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    visitor_name = models.CharField(max_length=32, default="")
    visitor_identity = models.CharField(max_length=32, default="")
    visit_time = models.DateTimeField()
    phone_number = models.CharField(max_length=32, default="")
    code = models.CharField(max_length=32, default="")
    is_valid = models.BooleanField(default=True)
    company_name = models.CharField(max_length=32, default="")
