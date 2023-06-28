from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.task import update_rent_message
from .models import *
import random
import string
import datetime
from user.models import User


def generate_random_string(length):
    # 生成包含数字和大写字母的可选字符集
    chars = string.digits + string.ascii_uppercase
    # 随机选择并连接字符集中的字符，生成随机字符串
    return ''.join(random.choices(chars, k=length))


# 管理员导入租赁信息
@csrf_exempt  # 跨域设置
def add_rent_record(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        room_names = request.POST.getlist('room_names')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        sign_time = request.POST.get('sign_time')
        expire_time = start_time
        users = User.objects.filter(user_id=user_id, is_delete=False)
        order_id = generate_random_string(10)
        date_format = '%Y-%m-%d'
        start_time = datetime.datetime.strptime(start_time, date_format)
        end_time = datetime.datetime.strptime(end_time, date_format)
        if end_time < datetime.datetime.today():
            return JsonResponse({'error': '1005', 'msg': '租赁时间不合法'})
        sign_time = datetime.datetime.strptime(sign_time, date_format)
        expire_time = datetime.datetime.strptime(expire_time, date_format)
        user = users.first()
        room_names = room_names[0].split(',')
        room_list = room_names[1::2]
        for room_name in room_list:
            rooms = Room.objects.filter(room_name=room_name)
            room = rooms.first()
            room.is_empty = False
            room.save()
            rent = Rent(order_id=order_id, user_id=user.user_id, room_id=room.room_id, start_time=start_time,
                        end_time=end_time, sign_time=sign_time, expire_time=expire_time)
            rent.save()
        return JsonResponse({'error': '0', 'msg': '导入租赁信息成功', 'room_names': room_list})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 管理员填写缴费信息
@csrf_exempt
def add_payment_record(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        # 续费时间精确到天
        pay_time = request.POST.get('pay_time')
        date_format = '%Y-%m-%d'
        pay_time = datetime.datetime.strptime(pay_time, date_format)

        rents = Rent.objects.filter(order_id=order_id, is_delete=False)
        if not rents.exists():
            return JsonResponse({'error': '1002', 'msg': '订单不存在'})
        rent1 = rents.first()
        if rent1.expire_time >= rent1.end_time:
            return JsonResponse({'error': '1003', 'msg': '订单已经缴费'})
        payment_record = PaymentRecord(order_id=order_id, pay_time=pay_time, is_delete=False)
        payment_record.save()

        for rent in rents:
            # 将expire_time更新至原来时间的一年后,但不能超过end_time
            expire_time = rent.expire_time.replace(year=rent.expire_time.year + 1)
            rent.expire_time = min(expire_time, rent.end_time)
            rent.save()
        return JsonResponse({'error': '0', 'msg': '缴费成功'})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 获取楼层总数
@csrf_exempt
def get_floor_count(request):
    if request.method == 'GET':
        # 从room表中获取floor字段的最大值
        floor_count = Room.objects.order_by('-floor')[0].floor
        return JsonResponse({'error': '0', 'floor_count': floor_count})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 获取楼层的房间状态
@csrf_exempt
def get_room_status_by_floor(request):
    if request.method == 'POST':
        floor = request.POST.get('floor')
        room_list = Room.objects.filter(floor=floor)
        room_status_list = []
        for room in room_list:
            room_status_list.append({'room_id': room.room_id, 'room_name': room.room_name, 'is_empty': room.is_empty})
        return JsonResponse({'error': '0', 'msg': '获取楼层的房间状态', 'data': room_status_list})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 获取空房间
@csrf_exempt
def get_empty_room(request):
    if request.method == 'POST':
        data = []
        for i in range(1, 13):
            room_list = Room.objects.filter(floor=i, is_empty=True)
            children = []
            for room in room_list:
                children.append({'value': room.room_name, 'label': room.room_name})
            data.append({'value': i, 'label': str(i) + '楼', 'children': children})
        return JsonResponse({'error': '0', 'msg': '获取空房间', 'data': data})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 获取房间的租赁信息
@csrf_exempt
def get_rent_info_by_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room = Room.objects.filter(room_name=room_name)
        rent = Rent.objects.filter(room_id=room.first().room_id, is_delete=False)
        room_info_list = []
        for r in rent:
            order_id = r.order_id
            user_id = r.user_id
            start_time = r.start_time
            end_time = r.end_time
            sign_time = r.sign_time
            expire_time = r.expire_time
            user = User.objects.filter(user_id=user_id)
            if not user.exists():
                return JsonResponse({'error': '1002', 'msg': '用户不存在'})
            user = user.first()
            if start_time < datetime.date.today() < end_time:
                is_rented = True
            else:
                is_rented = False
            room_info_list.append({
                'order_id': order_id,
                'user': {
                    'user_id': user_id,
                    'username': user.username,
                    'email': user.email,
                    'legal_entity_name': user.legal_entity_name,
                    'company_name': user.company_name,
                    'contact_person': user.contact_person,
                    'contact_phone': user.contact_phone,
                },
                'start_time': start_time,
                'end_time': end_time,
                'sign_time': sign_time,
                'expire_time': expire_time,
                'is_rented': is_rented,
            })
        # 将数组room_info_list按照sign_time降序排列
        room_info_list.sort(key=lambda x: x['sign_time'], reverse=True)
        return JsonResponse({'error': '0', 'msg': '获取房屋租赁信息', 'data': room_info_list})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 根据user_id获取缴费信息
@csrf_exempt
def get_payment_record_by_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        payment_data = []
        # 根据rent表的order_id字段去重
        rent_list = Rent.objects.filter(user_id=user_id, is_delete=False)
        list = []
        order_list = []
        for rent in rent_list:

            if rent.order_id in list:
                continue
            list.append(rent.order_id)
            order_list.append({'value': rent.order_id, 'label': rent.order_id})
            data = get_rent_list(rent)
            # 将数组data中的元素添加到payment_data中
            payment_data.extend(data)
        # 把payment_datat按照订单号order_id正序和缴费周期payment_cycle倒序进行排序
        payment_data = sorted(payment_data, key=lambda x: (x['order_id'], x['payment_cycle']), reverse=True)
        return JsonResponse({'error': '0', 'msg': '获取缴费信息', 'data': payment_data, 'order_list': order_list})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 修改租赁信息
@csrf_exempt
def modify_rent_info(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        sign_time = request.POST.get('sign_time')
        rent = Rent.objects.filter(order_id=order_id, is_delete=False)
        if not rent:
            return JsonResponse({'error': '1', 'msg': '订单号不存在'})
        for r in rent:
            r.start_time = start_time
            r.end_time = end_time
            r.sign_time = sign_time
            r.expire_time = start_time
            r.save()
        return JsonResponse({'error': '0', 'msg': '修改租赁信息成功'})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 删除租赁信息
@csrf_exempt
def delete_rent_info(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        rent = Rent.objects.filter(order_id=order_id, is_delete=False)
        if not rent:
            return JsonResponse({'error': '1', 'msg': '订单号不存在'})
        for r in rent:
            r.is_delete = True
            r.save()
            room = Room.objects.get(room_id=r.room_id)
            room.is_empty = True
            room.save()
        for payment_record in PaymentRecord.objects.filter(order_id=order_id, is_delete=False):
            payment_record.is_delete = True
            payment_record.save()
        return JsonResponse({'error': '0', 'msg': '删除租赁信息成功'})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 修改缴费信息
@csrf_exempt
def modify_payment_info(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        order_id = request.POST.get('order_id')
        pay_time = request.POST.get('pay_time')
        payment = PaymentRecord.objects.filter(payment_record_id=payment_id)
        if not payment:
            return JsonResponse({'error': '1001', 'msg': '无法修改不存在的缴费信息'})
        payment = payment.first()
        if payment.is_delete:
            return JsonResponse({'error': '1002', 'msg': '无法修改已删除的缴费信息'})
        payment.order_id = order_id
        payment.pay_time = pay_time
        payment.save()
        return JsonResponse({'error': '0', 'msg': '修改缴费信息成功'})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 删除缴费信息
@csrf_exempt
def delete_payment_info(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        payment = PaymentRecord.objects.filter(payment_record_id=payment_id)
        payment = payment.first()
        if not payment:
            return JsonResponse({'error': '1001', 'msg': '无法删除不存在的缴费信息'})
        payment.is_delete = True
        payment.save()
        return JsonResponse({'error': '0', 'msg': '删除缴费信息成功'})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


# 根据user_id获取公司信息和租赁房间信息
@csrf_exempt
def get_company_info(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id, is_delete=False)
        user = users.first()
        company_name = user.company_name
        rents = Rent.objects.filter(user_id=user_id, is_delete=False, is_useful=True)
        room_data = []
        for rent in rents:
            rooms = Room.objects.filter(room_id=rent.room_id)
            room = rooms.first()
            room_data.append({
                'room_id': room.room_id,
                'room_name': room.room_name,
            })
        return JsonResponse({'error': '0', 'msg': '获取公司信息和租赁房间信息成功', 'company_name': company_name, 'room_data': room_data})
    else:
        return JsonResponse({'error': '1', 'msg': '请求方法错误'})


def get_rent_list(rent):
    data = []
    order_id = rent.order_id
    payment_record_list = PaymentRecord.objects.filter(order_id=order_id, is_delete=False)
    start = rent.start_time
    end = start.replace(year=start.year + 1)
    for payment_record in payment_record_list:
        start_month = str(start.month)
        if len(start_month) == 1:
            start_month = '0' + str(start.month)
        end_month = str(end.month)
        if len(end_month) == 1:
            end_month = '0' + str(end.month)
        pay_time = payment_record.pay_time
        data.append({
            'order_id': order_id,
            'payment_cycle': str(start.year) + '-' + start_month + '~' + str(end.year) + '-' + end_month,
            'payment_id': payment_record.payment_record_id,
            'pay_time': pay_time,
            'is_pay': '是',
        })
        start = end
        end = start.replace(year=start.year + 1)
    while end <= rent.end_time:
        start_month = str(start.month)
        if len(start_month) == 1:
            start_month = '0' + str(start.month)
        end_month = str(end.month)
        if len(end_month) == 1:
            end_month = '0' + str(end.month)
        data.append({
            'order_id': order_id,
            'payment_cycle': str(start.year) + '-' + start_month + '~' + str(end.year) + '-' + end_month,
            'payment_id': '',
            'pay_time': '',
            'is_pay': '否',
        })
        start = end
        end = start.replace(year=start.year + 1)
    if start < rent.end_time:
        end = rent.end_time
        start_month = str(start.month)
        if len(start_month) == 1:
            start_month = '0' + str(start.month)
        end_month = str(end.month)
        if len(end_month) == 1:
            end_month = '0' + str(end.month)
        data.append({
            'order_id': order_id,
            'payment_cycle': str(start.year) + '-' + start_month + '~' + str(end.year) + '-' + end_month,
            'payment_id': '',
            'pay_time': '',
            'is_pay': '否',
        })
    return data


@csrf_exempt
def flush_room_status(request):
    if request.method == 'POST':
        update_rent_message()
        return JsonResponse({'error': '0', 'msg': '已刷新'})
    else:
        return JsonResponse({'error': '100001', 'msg': '请求方法错误'})
