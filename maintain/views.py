# Create your views here.
import random

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from space.models import Room
from .models import *
from .serializers import MaintainSerialize
from message.utils import *

import joblib
import pandas as pd
import jieba
import jieba.analyse
import re

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier


# 用户通过系统报修
@csrf_exempt  # 跨域设置
def report(request):
    if request.method == 'POST':
        problem = request.POST.get('desc')
        room_name = request.POST.get('roomId')
        user_id = request.POST.get('user_id')
        company_name = request.POST.get('companyName')
        contact_person = request.POST.get('username')
        contact_phone = request.POST.get('phone')
        maintain_time = request.POST.get('time')
        if problem and room_name and user_id:
            try:
                room = Room.objects.get(room_name=room_name)
                user = User.objects.get(user_id=user_id)
                MaintenanceRecord.objects.create(
                    problem=problem,
                    room_id=room.room_id,
                    room_name=room.room_name,
                    user_id=user_id,
                    company_name=company_name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    maintain_time=maintain_time,
                    status='report'
                )
                send_notification_user_to_admin(user, "发起维修工单", "")
                return JsonResponse({'error': '0', 'msg': '报修成功'})
            except Exception as e:
                print(e)
                return JsonResponse({'error': '1002', 'msg': '报修失败'})
        else:
            return JsonResponse({'error': '1001', 'msg': '参数错误'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 管理员根据状态获取维修工单
@csrf_exempt  # 跨域设置
def get_report(request):
    if request.method == 'POST':
        report_status = request.POST.get('status')
        if report_status == 'all':
            maintenance_records = MaintenanceRecord.objects.all()
        elif report_status == 'dispatched':
            maintenance_records = MaintenanceRecord.objects.filter(status__in=['dispatched', 'repairing'])
        else:
            maintenance_records = MaintenanceRecord.objects.filter(status=report_status)
        if not maintenance_records.exists():
            return JsonResponse({'error': '0', 'msg': '不存在对应状态的工单', 'data': []})
        data = []
        for maintenance_record in maintenance_records:
            if maintenance_record.maintain_user_id == -1:
                maintenance_user_name = ""
            else:
                maintenance_user_name = User.objects.get(user_id=maintenance_record.maintain_user_id).contact_person
            data.append({
                'maintenance_record_id': maintenance_record.maintenance_record_id,
                'problem': maintenance_record.problem,
                'commit_time': maintenance_record.commit_time,
                'room_id': maintenance_record.room_id,
                'room_name': maintenance_record.room_name,
                'user_id': maintenance_record.user_id,
                'company_name': maintenance_record.company_name,
                'contact_person': maintenance_record.contact_person,
                'contact_phone': maintenance_record.contact_phone,
                'maintain_time': maintenance_record.maintain_time,
                'maintain_user_id': maintenance_record.maintain_user_id,
                'maintain_user_name': maintenance_user_name,
                'solution': maintenance_record.solution,
                'solve_time': maintenance_record.solve_time,
                'status': maintenance_record.status,
            })
        return JsonResponse({'error': '0',
                             'msg': '获取工单成功',
                             # 'data': MaintainSerialize(maintenance_records, many=True).data
                             'data': data
                             })
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 用户获取维修工单
@csrf_exempt  # 跨域设置
def get_report_by_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.filter(user_id=user_id,
                                   is_delete=False)
        if not user.exists():
            return JsonResponse({'error': '1002', 'msg': '用户不存在'})
        maintenance_records = []
        maintenance_record = MaintenanceRecord.objects.filter(user_id=user_id, status='report')
        if maintenance_record.exists():
            maintenance_records.extend(maintenance_record)
        maintenance_record = MaintenanceRecord.objects.filter(user_id=user_id, status='dispatched')
        if maintenance_record.exists():
            maintenance_records.extend(maintenance_record)
        maintenance_record = MaintenanceRecord.objects.filter(user_id=user_id, status='repairing')
        if maintenance_record.exists():
            maintenance_records.extend(maintenance_record)
        maintenance_record = MaintenanceRecord.objects.filter(user_id=user_id, status='repaired')
        if maintenance_record.exists():
            maintenance_records.extend(maintenance_record)
        return JsonResponse({'error': '0',
                             'msg': '获取工单成功',
                             'data': MaintainSerialize(maintenance_records, many=True).data
                             })

    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 管理员获取可用的维修人员
# 该接口被弃用，在user模块中实现
# @csrf_exempt  # 跨域设置
# def get_free_maintainer(request):
#     if request.method == 'POST':
#         try:
#             users = User.objects.filter(identity='维修人员', is_working=False)
#             data = []
#             if len(users) == 0:
#                 return JsonResponse({'error': '0', 'msg': '没有可用的维修人员'})
#             for user in users:
#                 data.append({
#                     'user_id': user.user_id,
#                     'username': user.username,
#                     'job_category': user.job_category,
#                     'is_working': user.is_working,
#                 })
#             return JsonResponse({'error': '0', 'msg': '获取维修人员成功', 'data': data})
#         except Exception as e:
#             return JsonResponse({'error': '1002', 'msg': '获取维修人员失败'})
#     else:
#         return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 管理员派发维修任务
@csrf_exempt  # 跨域设置
def dispatch(request):
    if request.method == 'POST':
        maintenance_record_id = request.POST.get('maintenance_record_id')
        maintain_user_ids = request.POST.getlist('maintain_user_id')
        maintain_user_id = maintain_user_ids[0].split(',')[1]

        if maintenance_record_id and maintain_user_id:
            maintenance_record = MaintenanceRecord.objects.filter(maintenance_record_id=maintenance_record_id,
                                                                  status='report')
            if not maintenance_record.exists():
                return JsonResponse({'error': '1001', 'msg': '维修工单不存在'})
            maintenance_record = maintenance_record.first()
            maintainer = User.objects.filter(user_id=maintain_user_id,
                                             is_delete=False,
                                             is_working=False)
            if not maintainer.exists():
                return JsonResponse({'error': '1002', 'msg': '维修员不存在'})
            maintainer = maintainer.first()
            maintenance_record.maintain_user_id = maintain_user_id
            maintenance_record.status = 'dispatched'
            maintenance_record.save()
            maintainer.is_working = True
            maintainer.save()
            user = User.objects.filter(user_id=maintenance_record.user_id,
                                       is_delete=False)
            if not user.exists():
                return JsonResponse({'error': '1003', 'msg': '用户不存在'})
            user = user.first()
            # 给维修人员发送通知
            send_notification_admin_to_user(maintainer, '新的维修工单！', '您有待处理的维修工单。')
            # 给用户发送通知
            msg = '您的维修工单已派发。\n维修人员：' + maintainer.contact_person + '\n联系方式：' + maintainer.contact_phone + \
                  '\n维修时间：' + maintenance_record.maintain_time + '\n请您耐心等待。'
            send_notification_admin_to_user(user, '维修工单派发通知', msg)
            return JsonResponse({'error': '0', 'msg': '派发成功'})
        else:
            return JsonResponse({'error': '1003', 'msg': '参数错误'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 管理员发送反馈
@csrf_exempt  # 跨域设置
def feedback(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        info = request.POST.get('info')
        user = User.objects.filter(user_id=user_id,
                                   is_delete=False)
        if not user.exists():
            return JsonResponse({'error': '1002', 'msg': '用户不存在'})
        user = user.first()
        send_notification_admin_to_user(user, '维修工单反馈信息通知', info)
        return JsonResponse({'error': '0', 'msg': '反馈发送成功'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 维修人员获取当前维修任务
@csrf_exempt  # 跨域设置
def get_task(request):
    if request.method == 'POST':
        maintainer_id = request.POST.get('maintain_user_id')
        maintain_list_status = request.POST.get('status')
        if maintain_list_status == 'all':
            maintenance_records = MaintenanceRecord.objects.filter(maintain_user_id=maintainer_id, status='repaired')
        else:
            # 查询表中status为dispatched或者repairing的数据
            maintenance_records = MaintenanceRecord.objects.filter(status__in=['dispatched', 'repairing'], maintain_user_id=maintainer_id)
        if len(maintenance_records) == 0:
            return JsonResponse({'error': '0', 'msg': '没有已派发的工单'})
        data = []
        for maintenance_record in maintenance_records:
            solve_time = str(maintenance_record.solve_time)
            data.append({
                'maintenance_record_id': maintenance_record.maintenance_record_id,
                'problem': maintenance_record.problem,
                'commit_time': maintenance_record.commit_time,
                'room_id': maintenance_record.room_id,
                'room_name': maintenance_record.room_name,
                'user_id': maintenance_record.user_id,
                'company_name': maintenance_record.company_name,
                'contact_person': maintenance_record.contact_person,
                'contact_phone': maintenance_record.contact_phone,
                'maintain_time': maintenance_record.maintain_time,
                'maintain_user_id': maintenance_record.maintain_user_id,
                # 'maintain_user_name': maintenance_user_name,
                'solution': maintenance_record.solution,
                'solve_time': solve_time,
                'status': maintenance_record.status,
            })
        return JsonResponse({'error': '0',
                             'msg': '获取任务成功',
                             'data': data})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 维修人员接收当前维修任务,修改状态为repairing
@csrf_exempt  # 跨域设置
def accept_task(request):
    if request.method == 'POST':
        maintenance_record_id = request.POST.get('maintenance_record_id')
        maintain_user_id = request.POST.get('maintain_user_id')
        maintenance_record = MaintenanceRecord.objects.filter(maintenance_record_id=maintenance_record_id)
        if not maintenance_record.exists():
            return JsonResponse({'error': '1001', 'msg': '维修工单不存在'})
        maintenance_record = maintenance_record.first()
        if str(maintenance_record.maintain_user_id) != str(maintain_user_id):
            return JsonResponse({'error': '1002', 'msg': '维修工单不属于该维修人员'})
        maintenance_record.status = 'repairing'
        maintenance_record.save()
        return JsonResponse({'error': '0', 'msg': '接受任务成功'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 维修人员填写维修工单的最终状态
@csrf_exempt  # 跨域设置
def after_task(request):
    if request.method == 'POST':
        maintenance_record_id = request.POST.get('maintenance_record_id')
        solve_time = request.POST.get('solve_time')
        solution = request.POST.get('solution')
        maintenance_record = MaintenanceRecord.objects.filter(maintenance_record_id=maintenance_record_id)
        if not maintenance_record.exists():
            return JsonResponse({'error': '1001', 'msg': '维修工单不存在'})
        maintenance_record = maintenance_record.first()
        maintenance_record.solution = solution
        maintenance_record.solve_time = solve_time
        maintenance_record.status = 'repaired'
        maintenance_record.save()
        user = User.objects.filter(user_id=maintenance_record.maintain_user_id,
                                   is_delete=False)
        if not user.exists():
            return JsonResponse({'error': '1002', 'msg': '维修人员不存在'})
        user = user.first()
        user.is_working = False
        user.save()
        return JsonResponse({'error': '0', 'msg': '维修工单已完成'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 洗数据
@csrf_exempt  # 跨域设置
def wash_data(request):
    # maintenance_record 表 maintain_time 列
    # 将 形如 2023-06-06 13:15:57.000000 改为 2023-06-06 12:00 ~ 2023-06-06 14:00
    if request.method == 'POST':
        try:
            maintenance_records = MaintenanceRecord.objects.all()
            for maintenance_record in maintenance_records:
                maintain_time = maintenance_record.maintain_time
                # 判断maintain_time是否包含字符'-'
                if '-' in maintain_time:
                    continue
                if maintain_time:
                    maintain_time = maintain_time.strftime("%Y-%m-%d %H:%M")
                    maintain_time = maintain_time.split(' ')
                    hour = maintain_time[1].split(':')[0]
                    hour = int(hour) // 2 * 2
                    end_hour = hour + 2
                    # 2023-06-24 08:00:00-10:00:00
                    new_maintain_time = maintain_time[0] + ' ' + hour + ':00:00' + '-' + end_hour + ':00:00'
                    maintenance_record.maintain_time = new_maintain_time
                    maintenance_record.save()
            return JsonResponse({'error': '0', 'msg': '洗数据成功'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': '1002', 'msg': '洗数据失败'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 训练模型，用于智能派单
@csrf_exempt  # 跨域设置
def train_model(request):
    if request.method == 'POST':
        csv_file = 'maintain/data.csv'
        # 读取数据
        data = pd.read_csv(csv_file, encoding='utf-8')

        # 数据清洗
        # 去除空值
        data.dropna(inplace=True)
        # 去除重复值
        data.drop_duplicates(inplace=True)
        # 去除停用词
        stopwords = pd.read_csv('maintain/stopwords.txt', index_col=False, quoting=3, sep="\t", names=['stopword'],
                                encoding='utf-8')
        data['content'] = data['content'].apply(
            lambda x: ' '.join([word for word in x.split() if word not in stopwords]))
        # 去除标点符号
        data['content'] = data['content'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
        # 去除数字
        data['content'] = data['content'].apply(lambda x: re.sub(r'[0-9]', '', x))
        # 去除空格
        data['content'] = data['content'].apply(lambda x: re.sub(r'\s+', '', x))

        # 分词
        data['content'] = data['content'].apply(lambda x: ' '.join(jieba.cut(x)))
        # print(data['content'])

        # 特征提取 TF-IDF
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(data['content']))

        # 训练模型
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(tfidf, data['type'])

        # 保存模型
        joblib.dump(clf, 'maintain/model.pkl')
        joblib.dump(vectorizer, 'maintain/vectorizer.pkl')
        joblib.dump(transformer, 'maintain/transformer.pkl')

        return JsonResponse({'error': '0', 'msg': '模型训练成功'})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 调用模型，智能派单
@csrf_exempt  # 跨域设置
def smart_dispatch(request):
    if request.method == 'POST':
        maintenance_record_id = request.POST.get('maintenance_record_id')
        maintenance_records = MaintenanceRecord.objects.filter(maintenance_record_id=maintenance_record_id)
        if not maintenance_records.exists():
            return JsonResponse({'error': '1001', 'msg': '维修工单不存在'})
        maintenance_record = maintenance_records.first()
        problem = maintenance_record.problem

        # 加载模型
        clf = joblib.load('maintain/model.pkl')
        vectorizer = joblib.load('maintain/vectorizer.pkl')
        transformer = joblib.load('maintain/transformer.pkl')

        test_data = [problem]
        test_data = [' '.join(jieba.cut(x)) for x in test_data]
        # 特征提取
        test_tfidf = transformer.transform(vectorizer.transform(test_data))
        # 预测
        result = clf.predict(test_tfidf)
        print(result[0])
        if result[0] == '清洁':
            job_category = '清洁工'
        else:
            job_category = '维修人员（' + result[0] + '）'
        workers = User.objects.filter(identity='worker', is_delete=False, is_working=False, job_category=job_category)
        count = len(workers)
        if count == 0:
            return JsonResponse({'error': '1002', 'msg': '没有空闲的维修人员', 'type': result[0]})
        random_count = random.randint(1, count)
        maintainer = workers[random_count - 1]

        maintenance_record = MaintenanceRecord.objects.filter(maintenance_record_id=maintenance_record_id,
                                                              status='report')
        if not maintenance_record.exists():
            return JsonResponse({'error': '1001', 'msg': '维修工单不存在'})
        maintenance_record = maintenance_record.first()

        maintenance_record.maintain_user_id = maintainer.user_id
        maintenance_record.status = 'dispatched'
        maintenance_record.save()
        maintainer.is_working = True
        maintainer.save()

        user = User.objects.filter(user_id=maintenance_record.user_id,
                                   is_delete=False)
        if not user.exists():
            return JsonResponse({'error': '1003', 'msg': '用户不存在'})
        user = user.first()
        # 给维修人员发送通知
        send_notification_admin_to_user(maintainer, '新的维修工单！', '您有待处理的维修工单。')
        # 给用户发送通知
        msg = '您的维修工单已派发。\n维修人员：' + maintainer.contact_person + '\n联系方式：' + maintainer.contact_phone + \
              '\n维修时间：' + maintenance_record.maintain_time + '\n请您耐心等待。'
        send_notification_admin_to_user(user, '维修工单派发通知', msg)

        return JsonResponse({'error': '0', 'msg': '智能派单成功', 'maintain_user_id': maintainer.user_id,
                             'maintain_user_name': maintainer.contact_person, 'job_category': job_category})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})


# 按类型获取维修人员
@csrf_exempt  # 跨域设置
def get_maintainer_by_type(request):
    if request.method == 'POST':
        workers = User.objects.filter(identity='worker', is_delete=False, is_working=False)
        # 对workers 的job_category进行筛选，筛选出工种为维修人员（电）,维修人员（水），维修人员（机械）的人员，分别以列表形式返回
        worker_electric = []
        worker_water = []
        worker_mechanical = []
        worker_clean = []
        for worker in workers:
            if worker.job_category == '维修人员（电）':
                worker_electric.append({'value': worker.user_id, 'label': worker.contact_person})
            elif worker.job_category == '维修人员（水）':
                worker_water.append({'value': worker.user_id, 'label': worker.contact_person})
            elif worker.job_category == '维修人员（机械）':
                worker_mechanical.append({'value': worker.user_id, 'label': worker.contact_person})
            elif worker.job_category == '清洁工':
                worker_clean.append({'value': worker.user_id, 'label': worker.contact_person})
        data = [{'value': '1', 'label': '维修人员（电）', 'children': worker_electric},
                {'value': '2', 'label': '维修人员（水）', 'children': worker_water},
                {'value': '3', 'label': '维修人员（机械）', 'children': worker_mechanical},
                {'value': '4', 'label': '清洁工', 'children': worker_clean}]
        return JsonResponse({'error': '0',
                             'msg': '获取维修人员成功',
                             'data': data})
    else:
        return JsonResponse({'error': '1001', 'msg': '请求方式错误'})
