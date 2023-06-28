import datetime

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import date

from user.models import User
from user.serializers import WorkerSerialize, UserSerialize
from utils.token import get_user_id, create_token
from space.models import Rent, Room


# Create your views here.

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        users = User.objects.filter(username=username, is_delete=False)
        if users.exists():
            user = users.first()
            if user.password == password:
                token = create_token(user.user_id)
                print("success")
                return JsonResponse({
                    'errno': 0,
                    'msg': "登录成功",
                    'data': {
                        'authorization': token
                    },
                    'user_id': get_user_id(token),
                    'identity': user.identity
                })
            else:
                return JsonResponse({'errno': 100003, 'msg': "密码错误"})
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def register(request):
    # 添加用户
    if request.method == 'POST':
        username = request.POST.get('username')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        email = request.POST.get('email')
        identity = request.POST.get('identity')  # 获得注册用户身份
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')

        users = User.objects.filter(username=username, is_delete=False)
        if users.exists():
            return JsonResponse({'errno': 300001, 'msg': "用户名已注册"})
        if password_1 != password_2:
            return JsonResponse({'errno': 300002, 'msg': "两次输入的密码不一致"})

        users = User.objects.filter(email=email, is_delete=False)
        if users.exists():
            return JsonResponse({'errno': 300003, 'msg': "该邮箱已注册"})

        if identity == "user":
            legal_name = request.POST.get('legal_name')
            company_name = request.POST.get('company_name')
            User.objects.create(username=username,
                                password=password_1,
                                email=email,
                                identity=identity,
                                legal_entity_name=legal_name,
                                contact_person=contact_person,
                                company_name=company_name,
                                contact_phone=contact_phone)
        elif identity == "worker":
            job_category = request.POST.get('job_category')
            User.objects.create(username=username,
                                password=password_1,
                                email=email,
                                identity=identity,
                                contact_person=contact_person,
                                contact_phone=contact_phone,
                                job_category=job_category)

        return JsonResponse({'errno': 0, 'msg': "创建用户成功"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


# 查看用户的详细信息
@csrf_exempt
def user_info(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        admin_id = request.GET.get('admin_id')
        # 鉴权 查User表的identity字段
        identity = User.objects.filter(user_id=admin_id, is_delete=False).first().identity
        if identity != '管理员':
            return JsonResponse({'errno': 100002, 'msg': "权限不足"})
        users = User.objects.filter(user_id=user_id, is_delete=False)
        if users.exists():
            user = users.first()
            # TODO: 详细信息需要补充租赁信息，根据前端的需求进行修改
            return JsonResponse({
                'errno': 0,
                'msg': "成功",
                'data': {
                    user.to_dict()
                }
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


# 更新当前登录用户的信息
@csrf_exempt
def update_user_info(request):
    if request.method == 'POST':
        # TODO 这里需要把编辑用户信息界面的全部信息重传进来
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id, is_delete=False)
        if users.exists():
            user = users.first()
            user.legal_entity_name = request.POST.get('legal_entity_name')
            user.company_name = request.POST.get('company_name')
            user.contact_person = request.POST.get('contact_person')
            user.contact_phone = request.POST.get('contact_phone')
            user.save()
            return JsonResponse({
                'errno': 0,
                'msg': "成功",
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def update_worker_info(request):
    # 修改维修人员信息
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        users = User.objects.filter(user_id=user_id, is_delete=False)
        if users.exists():
            password_1 = request.POST.get('password_1')
            password_2 = request.POST.get('password_2')
            if password_1 != password_2:
                return JsonResponse({'errno': 300002, 'msg': "两次输入的密码不一致"})
            user = users.first()
            user.password = password_1
            new_email = request.POST.get('email')
            if User.objects.filter(email=new_email).count() >= 2:
                return JsonResponse({'errno': 100005, 'msg': "邮箱已被注册"})
            user.email = new_email
            user.contact_person = request.POST.get('contact_person')
            user.contact_phone = request.POST.get('contact_phone')
            user.job_category = request.POST.get('job_category')
            user.save()
            return JsonResponse({
                'errno': 0,
                'msg': "成功",
                'data': {
                    'user': user.to_dict()
                }
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def information(request):
    # 获取用户详细信息
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)
        users = User.objects.filter(user_id=user_id, is_delete=False)
        if users.exists():
            user = users.first()
            print("success")
            return JsonResponse({
                'errno': 0,
                'msg': "查询用户信息成功",
                'data': {
                    'user_id': user.user_id,
                    'legal_entity_name': user.legal_entity_name,
                    'company_name': user.company_name,
                    'contact_person': user.contact_person,
                    'contact_phone': user.contact_phone
                },
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "用户不存在"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def worker_list(request):
    # 获取工作人员列表
    if request.method == 'POST':
        users = User.objects.filter(identity="worker", is_delete=False)
        if users.exists():
            print("success")
            print(users.count())
            return JsonResponse({
                'errno': 0,
                'msg': "查询工作人员信息成功",
                'worker': WorkerSerialize(users, many=True).data
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "无工作人员"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def user_list(request):
    # 获取用户列表
    if request.method == 'POST':
        users = User.objects.filter(identity="user", is_delete=False)
        if users.exists():
            print("success")
            print(users.count())
            return JsonResponse({
                'errno': 0,
                'msg': "查询用户信息成功",
                'num': users.count(),
                'worker': UserSerialize(users, many=True).data
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "未查询到用户"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def delete_user(request):
    # 删除用户
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(user_id=user_id, is_delete=False)
        except Exception as e:
            return JsonResponse({'errno': 100004, 'msg': "未查询到用户", 'data': {
                'result': False
            }})
        if user is not None:
            if user.identity == "worker" and user.is_working is True:
                return JsonResponse({
                    'errno': 100001,
                    'msg': "删除信息失败",
                    'data': {
                        'result': False
                    }
                })
            user.is_delete = True
            user.save()
            return JsonResponse({
                'errno': 0,
                'msg': "删除信息成功",
                'data': {
                    'result': True
                }
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "未查询到用户", 'data': {
                'result': False
            }})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误", 'data': {
            'result': False
        }})


@csrf_exempt
def search_worker(request):
    # 模糊查找工作人员
    if request.method == 'POST':
        key_word = request.POST.get('contact_person')
        user = User.objects.filter(contact_person__contains=key_word, is_delete=False, identity="worker")
        if user.exists():
            print("success")
            return JsonResponse({
                'errno': 0,
                'msg': "查找工作人员成功",
                'worker': WorkerSerialize(user, many=True).data
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "未查询到工作人员"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def search_user(request):
    # 模糊查找用户
    if request.method == 'POST':
        key_word = request.POST.get('contact_person')
        user = User.objects.filter(Q(contact_person__contains=key_word) |
                                   Q(legal_entity_name__contains=key_word) |
                                   Q(company_name__contains=key_word)).filter(is_delete=False, identity="user")
        if user.exists():
            print("success")
            return JsonResponse({
                'errno': 0,
                'msg': "搜索用户成功",
                'worker': UserSerialize(user, many=True).data
            })
        else:
            return JsonResponse({'errno': 100004, 'msg': "未查询到用户"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


# 用户根据user_id返回客户租赁相关信息，包括房间号、开始时间、结束时间、签约日期。
@csrf_exempt
def user_lease_info(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        rents = Rent.objects.filter(user_id=user_id, is_delete=False, is_useful=True)
        if rents.exists():
            order_set = set()
            for rent in rents:
                order_set.add(rent.order_id)
            rent_info = []
            for order_id in order_set:
                rooms = ""
                rents_select_by_order_id = Rent.objects.filter(order_id=order_id, is_delete=False)
                for rent in rents_select_by_order_id:
                    room_name = Room.objects.get(room_id=rent.room_id).room_name
                    rooms += str(room_name) + ", "
                rooms = rooms[:-2]
                rent_info.append(rents_select_by_order_id.first().change_room_to_all_room(rooms))
            return JsonResponse({
                'errno': 0,
                'msg': "查询租赁信息成功",
                'data': {
                    'rent_info': rent_info
                }
            })
        else:
            return JsonResponse({'errno': 1, 'msg': "未查询到租赁信息"})
    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})


@csrf_exempt
def date_7(request):
    if request.method == 'GET':
        # Get the current date
        current_date = date.today()

        # Create a list to store the dates
        date_list = []

        # Generate the list of dates for the next 7 days
        for i in range(1, 7):
            # Add the current date plus the iteration index (i) as timedelta
            new_date = current_date + datetime.timedelta(days=i)
            date_list.append(new_date)

        return JsonResponse({
            'errno': 0,
            'msg': "查询日期成功",
            'data': {
                'date': date_list
            }
        })

    else:
        return JsonResponse({'errno': 200001, 'msg': "请求方式错误"})
