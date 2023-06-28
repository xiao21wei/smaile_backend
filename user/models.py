from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    # 作为user模型主键
    username = models.CharField(max_length=32, default="")
    # 用户名
    password = models.CharField(max_length=32, default="")
    # 密码
    email = models.CharField(max_length=32, default="")
    # 联系邮箱
    identity = models.CharField(max_length=16, default="")
    # 身份：管理员、工作人员、租赁用户
    is_delete = models.BooleanField(default=False)
    # 账号是否已注销
    legal_entity_name = models.CharField(max_length=32, default="", null=True)
    # 法人名称
    company_name = models.CharField(max_length=32, default="", null=True)
    # 公司名称
    contact_person = models.CharField(max_length=32, default="")
    # 联系人名称
    contact_phone = models.CharField(max_length=32, default="")
    # 联系电话
    is_working = models.BooleanField(default=False)
    # 工作人员：状态是否空闲
    job_category = models.CharField(max_length=32, default="", null=True)
    # 工作人员：工种

    # to jason data
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'identity': self.identity,
            'is_delete': self.is_delete,
            'legal_entity_name': self.legal_entity_name,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'is_working': self.is_working,
            'job_category': self.job_category,
        }
