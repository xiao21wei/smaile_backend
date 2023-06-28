import calendar
import datetime

from django.db.models.functions import ExtractDay, TruncYear, TruncMonth, ExtractYear, ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from maintain.models import MaintenanceRecord
from message.models import Message, AppointmentRecord
from message.serializers import MessageSerialize, AppointmentSerialize
from message.utils import send_notification_user_to_admin, send_message_code, send_notification_system_to_user
from user.models import User
from user.serializers import WorkerSerialize, UserSerialize
from utils.token import get_user_id, create_token
from space.views import generate_random_string


# Create your views here.
@csrf_exempt
def user_message_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id,
                                    is_delete=False)
        if users.exists():
            user = users.first()
            messages = Message.objects.filter(recipient_id=user.user_id).order_by('-message_id')
            return JsonResponse({
                'errno': 0,
                'msg': "返回信息列表成功",
                'data': MessageSerialize(messages, many=True).data
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def user_message_reading(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id,
                                    is_delete=False)
        read_type = request.POST.get('read_type')
        if users.exists():
            if read_type == "single":
                message_id = request.POST.get('message_id')
                message = Message.objects.filter(message_id=message_id).first()
                message.status = "read"
                message.save()
            elif read_type == "all":
                message = Message.objects.filter(recipient_id=user_id, status="unread")
                for i in message:
                    i.status = "read"
                    i.save()
            return JsonResponse({
                'errno': 0,
                'msg': "信息已读成功",
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def user_message_send(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id,
                                    is_delete=False)
        if users.exists():
            user = users.first()
            send_notification_user_to_admin(user, "message", "")
            return JsonResponse({
                'errno': 0,
                'msg': "success",
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


# TODO: 编写相关功能
# @csrf_exempt
# def send_guest_short_message(request):
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         users = User.objects.filter(user_id=user_id)
#         if users.exists():
#             user = users.first()
#             send_notification_user_to_admin(user, "message", "")
#             return JsonResponse({
#                 'errno': 0,
#                 'msg': "success",
#             })
#         else:
#             return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
#     else:
#         return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def make_appointment(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        visitor_name = request.POST.get('visitor_name')
        visitor_identity = request.POST.get('visitor_identity')
        visit_time_date = request.POST.get('visit_time')
        date_obj = datetime.datetime.strptime(visit_time_date, '%Y-%m-%d %H:%M')
        # 添加秒数到 datetime.datetime 对象
        visit_time = date_obj.replace(second=0)
        phone_number = request.POST.get('phone_number')
        company_name = request.POST.get('company_name')
        code = generate_random_string(6)
        AppointmentRecord.objects.create(user_id=user_id, visitor_name=visitor_name,
                                         visitor_identity=visitor_identity, visit_time=visit_time,
                                         phone_number=phone_number, code=code, company_name=company_name)
        user = User.objects.filter(user_id=user_id,
                                   is_delete=False)
        if user.exists():
            user = user.first()
            time_delta = datetime.timedelta(minutes=30)
            target_time = date_obj - time_delta
            target_time_str = target_time.strftime('%Y-%m-%d %H:%M')
            send_notification_system_to_user(user, "预约成功通知", "您的预约已成功提交，动态密码将于 "
                                             + target_time_str + " 发送给" + phone_number + "，请注意查收。")
        return JsonResponse({
            'errno': 0,
            'msg': "预约成功",
        })
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def appointment_list(request):
    if request.method == 'POST':
        appointment_record = AppointmentRecord.objects.all()
        return JsonResponse({
            'errno': 0,
            'msg': "success",
            'data': AppointmentSerialize(appointment_record, many=True).data
        })
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def message_test(request):
    if request.method == 'POST':
        send_message_code(request.POST.get('phone'), "aaaaaa")
        return JsonResponse({
            'errno': 0,
            'msg': "success"
        })
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def appointment_statistics(request):
    if request.method == 'POST':
        today = datetime.datetime.today()
        start_date = today.replace(day=1)  # 当前月份的第一天

        records_count = []
        months = []
        for i in range(12):
            end_date = start_date + datetime.timedelta(
                days=calendar.monthrange(start_date.year, start_date.month)[1] - 1)

            monthly_records = AppointmentRecord.objects.filter(
                visit_time__gte=start_date,
                visit_time__lte=end_date
            ).annotate(
                day=ExtractDay('visit_time')
            ).values('day').annotate(count=Count('appointment_record_id')).order_by('day')

            month_count = {d['day']: d['count'] for d in monthly_records}

            # 创建一个嵌套的字典结构，保存每个月份中每天的记录数量
            daily_counts = {}
            for day in range(1, calendar.monthrange(start_date.year, start_date.month)[1] + 1):
                if day in month_count:
                    daily_counts[day] = month_count[day]
                else:
                    daily_counts[day] = 0

            records_count.append({
                'year_month': f"{start_date.year}-{start_date.month:02}",
                'count': AppointmentRecord.objects.filter(
                    visit_time__year=start_date.year,
                    visit_time__month=start_date.month
                ).count(),
                'daily_records': daily_counts
            })
            months.append(f"{start_date.year}-{start_date.month:02}")

            start_date = start_date - datetime.timedelta(days=calendar.monthrange(start_date.year, start_date.month)[1])

        return JsonResponse({
            'errno': 0,
            'msg': "success",
            'data': {
                'months': months,
                'record_count': records_count,
            }
        })
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def maintenance_statistics(request):
    if request.method == 'POST':
        current_date = datetime.date.today()
        start_date = current_date.replace(day=1) - datetime.timedelta(days=365)
        maintain_records = MaintenanceRecord.objects.exclude(maintain_user_id=-1)

        water_worker_list = User.objects.filter(job_category="维修人员（水）")\
            .values_list('user_id', flat=True)
        electric_worker_list = User.objects.filter(job_category="维修人员（电）")\
            .values_list('user_id', flat=True)
        mechanic_worker_list = User.objects.filter(job_category="维修人员（机械）")\
            .values_list('user_id', flat=True)
        cleaner_worker_list = User.objects.filter(job_category="清洁工")\
            .values_list('user_id', flat=True)

        water = maintain_records.filter(
            maintain_user_id__in=water_worker_list,
            commit_time__gte=start_date,
        )

        electric = maintain_records.filter(
            maintain_user_id__in=electric_worker_list,
            commit_time__gte=start_date,
        )

        mechanic = maintain_records.filter(
            maintain_user_id__in=mechanic_worker_list,
            commit_time__gte=start_date,
        )

        cleaner = maintain_records.filter(
            maintain_user_id__in=cleaner_worker_list,
            commit_time__gte=start_date,
        )

        water_data = []
        electric_data = []
        mechanic_data = []
        cleaner_data = []
        for i in range(12):
            year = current_date.year
            month = current_date.month - i
            if month <= 0:
                year -= 1
                month += 12
            record = water.filter(commit_time__year=year, commit_time__month=month).count()
            water_data.append({
                'year_month': f"{year}-{month:02}",
                'count': record})
            record = electric.filter(commit_time__year=year, commit_time__month=month).count()
            electric_data.append({
                'year_month': f"{year}-{month:02}",
                'count': record})
            record = mechanic.filter(commit_time__year=year, commit_time__month=month).count()
            mechanic_data.append({
                'year_month': f"{year}-{month:02}",
                'count': record})
            record = cleaner.filter(commit_time__year=year, commit_time__month=month).count()
            cleaner_data.append({
                'year_month': f"{year}-{month:02}",
                'count': record})

        return JsonResponse({
            'errno': 0,
            'msg': "success",
            'data': {
                'water': water_data,
                'electric': electric_data,
                'mechanic': mechanic_data,
                'cleaner': cleaner_data
            }
        })
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})
