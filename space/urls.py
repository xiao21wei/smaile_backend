from django.urls import path

from .views import *

urlpatterns = [
    # 管理员导入缴费信息
    path('add_payment_record', add_payment_record, name='add_payment_record'),
    # 管理员导入租赁信息
    path('add_rent_record', add_rent_record, name='add_rent_record'),
    # 获取楼层总数
    path('get_floor_count', get_floor_count, name='get_floor_count'),
    # 获取楼层的房间状态
    path('get_room_status_by_floor', get_room_status_by_floor, name='get_room_status_by_floor'),
    # 获取空房间
    path('get_empty_room', get_empty_room, name='get_empty_room'),
    # 获取房间的租赁信息
    path('get_rent_info_by_room', get_rent_info_by_room, name='get_rent_info_by_room'),
    # 根据user_id获取缴费信息
    path('get_payment_record_by_user', get_payment_record_by_user, name='get_payment_record_by_user'),
    # 修改租赁信息
    path('modify_rent_info', modify_rent_info, name='modify_rent_info'),
    # 删除租赁信息
    path('delete_rent_info', delete_rent_info, name='delete_rent_info'),
    # 修改缴费信息
    path('modify_payment_info', modify_payment_info, name='modify_payment_info'),
    # 删除缴费信息
    path('delete_payment_info', delete_payment_info, name='delete_payment_info'),
    # 根据user_id获取公司信息和租赁房间信息
    path('get_company_info', get_company_info, name='get_company_info'),
    # 刷新房间状态
    path('flush_room_status', flush_room_status),
]
