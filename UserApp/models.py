from logging import Manager

from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    class Meta:
        db_table="custom_user"
        verbose_name="User"
        verbose_name_plural="User"
#
# 代理user表
class SuperUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name="Super User"
        verbose_name_plural="Super User"