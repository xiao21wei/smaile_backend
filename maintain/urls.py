from django.urls import path

from .views import *

urlpatterns = [
    # 用户通过系统报修
    path('report', report, name='report'),
    # 用户获取自己的报修工单
    path('get_report_by_user', get_report_by_user, name='get_report_by_user'),
    # 管理员根据状态获取维修工单
    path('get_report', get_report, name='get_report'),
    # 管理员获取空闲维修人员
    # path('get_free_maintainer', get_free_maintainer, name='get_free_maintainer'),
    # 管理员派发维修任务
    path('dispatch', dispatch, name='dispatch'),
    # 管理员发送反馈‘
    path('feedback', feedback, name='feedback'),
    # 维修人员获取当前维修任务
    path('get_task', get_task, name='get_task'),
    # 维修人员接收当前维修任务,修改状态为repairing
    path('accept_task', accept_task, name='accept_task'),
    # 维修人员填写维修工单的最终状态
    path('after_task', after_task, name='after_task'),
    # 洗数据
    path('wash_data', wash_data, name='wash_data'),
    # 按类型获取维修人员
    path('get_maintainer_by_type', get_maintainer_by_type, name='get_maintainer_by_type'),
    # 训练模型，用于智能派单
    path('train_model', train_model, name='train_model'),
    # 调用模型，智能派单
    path('smart_dispatch', smart_dispatch, name='smart_dispatch'),
]

