import datetime

# from django.contrib.auth.models import User
from UserApp.models import CustomUser as User
from django.db import models
from django.utils.html import format_html


# Create your models here.

class DataModel(models.Model):
    publication=models.CharField(max_length=64,null=True,verbose_name="Publication")
    volcano=models.CharField(max_length=64,null=True,verbose_name="Volcano")
    eruption=models.CharField(max_length=1064,null=True,verbose_name="Eruption")
    data_doi=models.CharField(max_length=64,null=True,verbose_name="Data DOI")
    chemistry=models.CharField(max_length=64,null=True,verbose_name="Chemistry")
    bulk_sio2=models.CharField(max_length=64,null=True,verbose_name="Bulk SiO2 (wt. %)")
    bulk_na2o=models.CharField(max_length=64,null=True,verbose_name="Bulk Na2O+K2O (wt.%)")
    glass_sio2=models.CharField(max_length=64,null=True,verbose_name="Glass SiO2 (wt. %)")
    glass_na2o=models.CharField(max_length=64,null=True,verbose_name="Glass Na2O+K2O (wt.%)")
    chemistry_doi=models.CharField(max_length=64,null=True,verbose_name="Chemistry DOI")
    rock_experiment_type=models.CharField(max_length=64,null=True,verbose_name="Rock/experiment type")
    subaerial_submarine=models.CharField(max_length=64,null=True,verbose_name="Subaerial/submarine")
    eff_exp=models.CharField(max_length=64,null=True,verbose_name="Eff/exp")
    sample_no=models.CharField(max_length=64,null=True,verbose_name="Sample no.")
    bulk_porosity=models.CharField(max_length=64,null=True,verbose_name="Bulk porosity (%)")
    connected_porosity=models.CharField(max_length=64,null=True,verbose_name="Connected porosity (%)")
    connectivity=models.CharField(max_length=64,null=True,verbose_name="Connectivity")
    permeability_k1=models.CharField(max_length=64,null=True,verbose_name="Permeability (k1) (m-2)")
    permeability_k2=models.CharField(max_length=64,null=True,verbose_name="Permeability (k2) (m-1)")
    vesicle_number_density=models.CharField(max_length=64,null=True,verbose_name="vesicle number density (m-3)")
    s_polydispersivity=models.CharField(max_length=64,null=True,verbose_name="S (polydispersivity)")
    total_crystallinity=models.CharField(max_length=64,null=True,verbose_name="total crystallinity (%)")
    phenocrystallinity=models.CharField(max_length=64,null=True,verbose_name="phenocrystallinity (%)")
    microcrystallinity=models.CharField(max_length=64,null=True,verbose_name="microcrystallinity (%)")
    create_date=models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        verbose_name="Data Admin"
        verbose_name_plural="Data Admin"


class DataColumnName(models.Model):
    name=models.CharField(max_length=256)
    desc=models.CharField(max_length=256)
    cate=models.IntegerField(default=0) #0:仅作展示，1是筛选字段，2是数据字段。


class UserUploadModel(models.Model):
    user_id=models.IntegerField(default=0)
    status=models.IntegerField(default=0) #状态：0：待审核，1审核通过,-1：驳回
    url=models.FileField(default=2048,upload_to='static/file/')
    upload_date=models.DateTimeField(default=datetime.datetime.now(),verbose_name="verbose name")


    def username(self):
        u=User.objects.filter(id=self.user_id).first()
        if u is None:
            return "Unknow"
        return u.username
    username.short_description="user name"

    # pass_audit_str.allow_tags = True
    # pass_audit_str.short_description = 'option'
    class Meta:
        verbose_name="Review Admin"
        verbose_name_plural="Review Admin"


class LiteratureModel(models.Model):
    publication=models.CharField(max_length=64,verbose_name="Publication")
    pub_year=models.CharField(max_length=16,verbose_name="Pub Year")
    doi=models.CharField(max_length=256,verbose_name="DOI")
    title=models.CharField(max_length=200,verbose_name="Title")
    class Meta:
        verbose_name="Literature Admin"
        verbose_name_plural="Literature Admin"
class DataReviewModel(DataModel):
    class Meta:
        verbose_name = "图片新闻"
        verbose_name_plural = verbose_name
        proxy = True


class HistoryModel(models.Model):
    url=models.CharField(max_length=2048)
    name=models.CharField(max_length=2048)
    crt_date=models.DateTimeField()
    user_id=models.IntegerField(default=0)
    type=models.IntegerField(default=0) # 1是图片，2是文本






