from django.db import models


class MaintenanceRecord(models.Model):
    maintenance_record_id = models.AutoField(primary_key=True)  # 维修工单ID
    problem = models.CharField(max_length=255)  # 问题
    commit_time = models.DateTimeField(auto_now_add=True)  # 提交时间
    room_id = models.IntegerField()  # 房间号
    user_id = models.IntegerField()  # 联系人用户ID
    room_name = models.CharField(max_length=255)  # 房间名称
    company_name = models.CharField(max_length=255)  # 公司名称
    contact_person = models.CharField(max_length=255)  # 联系人
    contact_phone = models.CharField(max_length=255)  # 联系电话
    maintain_time = models.CharField(max_length=255)  # 维修时间
    maintain_user_id = models.IntegerField(default=-1)  # 维修人员ID -1代表未指派
    solution = models.CharField(max_length=255)  # 解决方案
    solve_time = models.DateTimeField(null=True)  # 解决时间
    status = models.CharField(default="report", max_length=32)  # 工单状态  report  dispatched  repairing  repaired
    is_delete = models.BooleanField(default=False)  # 是否删除

    class Meta:
        db_table = 'maintenance_record'  # 指明数据库表名
        verbose_name = '维修记录'  # 在admin站点中显示的名称
        verbose_name_plural = '维修记录'  # 显示的复数名称

    def __str__(self):
        return self.problem  # 显示问题

    def dict(self):
        return {
            "maintenance_record_id": self.maintenance_record_id,
            "problem": self.problem,
            "commit_time": self.commit_time,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "room_name": self.room_name,
            "company_name": self.company_name,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "maintain_time": self.maintain_time,
            "maintain_user_id": self.maintain_user_id,
            "solution": self.solution,
            "solve_time": self.solve_time,
            "status": self.status
        }
