import datetime
import logging
from datetime import date

from message.models import AppointmentRecord
from message.utils import send_message_code
from space.models import Rent, Room
from django.core.mail import send_mail
from user.models import User
from django.conf import settings


def update_rent_message():
    time = datetime.datetime.now()
    rent = Rent.objects.filter(is_delete=False, is_useful=True)
    time = date.today()
    for i in rent:
        if i.end_time < time:
            i.is_useful = False
            i.save()
            room = Room.objects.filter(room_id=i.room_id).first()
            room.is_empty = True
            room.save()
    print("\n["+str(time)+"] update rent message success!\n")


def send_message():
    time = datetime.datetime.now()
    appointments = AppointmentRecord.objects.filter(is_valid=True)
    for i in appointments:
        time_diff = datetime.timedelta(minutes=40)
        time_diff_2 = datetime.timedelta(minutes=20)
        # 计算目标时间 当前时间后30min
        target_time = time + time_diff
        # 目标时间2为预约时间后40min
        target_time_2 = i.visit_time + time_diff_2
        if time < i.visit_time <= target_time:
            send_message_code(i.phone_number, i.code)
        if time > target_time_2:
            i.is_valid = False
            i.save()
    print("\n["+str(time)+"] send message success!\n")


def send_email():
    rent = Rent.objects.filter(is_delete=False, is_useful=True)
    time = date.today()
    for i in rent:
        if i.end_time < time:
            # 超出时间则不发送
            pass
        elif (i.expire_time - time).days < 30:
            # 发送邮箱提醒
            user_id = i.user_id
            user = User.objects.filter(user_id=user_id)
            if not user.exists():
                continue
            user = user.first()
            email = user.email
            username = user.username
            room = Room.objects.filter(room_id=i.room_id).first()
            room_name = room.room_name

            subject = '来自Smile大厦的提醒'
            message = ''  # 没有内容的时候可以指定为空
            html_message = '<h1>%s, 您的房间%s即将到期</h1>请及时缴纳物业费<br/>' % (username, room_name)
            sender = settings.EMAIL_FROM
            receiver = [email]
            send_mail(subject, message, sender, receiver, html_message=html_message)
    print("\n["+str(time)+"] send email success!\n")
