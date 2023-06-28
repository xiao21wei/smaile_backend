from django.db import models


class Room(models.Model):
    room_id = models.IntegerField(primary_key=True)  # 房间ID
    floor = models.IntegerField()  # 楼层
    room_name = models.CharField(max_length=255)  # 房间名
    is_empty = models.BooleanField()  # 是否空闲

    class Meta:
        db_table = 'room'
        verbose_name = '房间'
        verbose_name_plural = '房间'

    def __str__(self):
        return self.room_name  # 显示房间名


class Rent(models.Model):
    rent_id = models.IntegerField(primary_key=True)  # 租赁ID
    order_id = models.CharField(max_length=255)  # 订单ID
    user_id = models.IntegerField()  # 用户ID
    room_id = models.IntegerField()  # 房间ID
    start_time = models.DateTimeField()  # 开始时间
    end_time = models.DateTimeField()  # 结束时间
    sign_time = models.DateTimeField()  # 签约时间
    expire_time = models.DateTimeField()  # 到期时间
    is_delete = models.BooleanField(default=False)  # 是否被删除
    is_useful = models.BooleanField(default=True)  # 是否有效，默认为True

    class Meta:
        db_table = 'rent'
        verbose_name = '租赁'
        verbose_name_plural = '租赁'

    def __str__(self):
        return self.order_id  # 显示订单ID

    def to_dict(self):
        room = Room.objects.filter(room_id=self.room_id).first()
        return {
            'rent_id': self.rent_id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'sign_time': self.sign_time,
            'expire_time': self.expire_time,
            'room_name': room.room_name
        }

    def change_room_to_all_room(self, rooms):
        return {
            'rent_id': self.rent_id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'room_ids': rooms,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'sign_time': self.sign_time,
            'expire_time': self.expire_time,
            'rooms': rooms
        }


class PaymentRecord(models.Model):
    payment_record_id = models.IntegerField(primary_key=True)  # 支付记录ID
    order_id = models.CharField(max_length=255)  # 订单ID
    pay_time = models.DateTimeField()  # 支付时间
    is_delete = models.BooleanField(default=False)  # 是否被删除

    class Meta:
        db_table = 'payment_record'
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'

    def __str__(self):
        return self.payment_record_id  # 显示支付记录ID

    def to_dict(self):
        return {
            'payment_record_id': self.payment_record_id,
            'order_id': self.order_id,
            'pay_time': self.pay_time,
        }
