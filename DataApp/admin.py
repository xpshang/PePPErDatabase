from django.contrib import admin
from simpleui.admin import AjaxAdmin
from django.urls import reverse

# Register your models here.
from .models import *
# 数量管理
class DataAdmin(admin.ModelAdmin):
    list_per_page = 50
    ordering = ("publication","volcano","eruption")
    list_display = ('publication','volcano','eruption','data_doi','chemistry','bulk_sio2','bulk_na2o','glass_sio2','glass_na2o','chemistry_doi','rock_experiment_type','subaerial_submarine','eff_exp','sample_no','bulk_porosity','connected_porosity','connectivity','permeability_k1','permeability_k2','vesicle_number_density','s_polydispersivity','total_crystallinity','phenocrystallinity','microcrystallinity','create_date')  # list
    List_display_links = None


    # readonly_fields = ['upload_id']
    def has_add_permission(self, request):
        # 禁用添加按钮
        return False
#审核页面
class ReviewAdmin(admin.ModelAdmin):
    list_per_page = 50


    list_display = ('id','username','url', 'upload_date','Status','Action')

    def has_add_permission(self, request):
        # 禁用添加按钮
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):

        qs = super(ReviewAdmin, self).get_queryset(request)
        return qs.order_by("-upload_date")
    # 状态值那一列根据不同的状态,返回不同的样式
    def Status(self,obj):
        if obj.status==-1:
            return format_html('<div style="width: 70px;height: 20px;line-height: 20px;text-align: center;color: white;background-color: #A0A2AF;padding: 5px;font-size: 14px;border-radius: 5px">Reject</div>')
        elif obj.status==1:
            return format_html("""<div style="width: 70px;height: 20px;line-height: 20px;text-align: center;color: white;background-color: #71D4BB;padding: 5px;font-size: 14px;border-radius: 5px">Approved</div>""")
        else:
            return format_html("""<div style="width: 70px;height: 20px;line-height: 20px;text-align: center;color: white;background-color: orange;padding: 5px;font-size: 14px;border-radius: 5px">Pending</div>""")
    def Action(self, obj):
        if obj.status==0:
            url ="/reviewsubmit/?id={}&type=reject".format(obj.id)
            # return format_html('<a class="button" href="{}">Approved</a>'.format(url))
            return format_html("""<a style="width: 70px;height: 20px;line-height: 20px;text-align: center;color: orange;border:2px solid #d76d3f;padding: 5px;font-size: 14px;border-radius: 5px;text-decoration: none" onclick="showInfo({})" href='javascript:void(0)' class="test_btn">Approve</a>
    <a style="width: 70px;height: 20px;line-height: 20px;text-align: center;color:orange;border:2px solid #d76d3f;padding: 5px;font-size: 14px;border-radius: 5px;text-decoration: none;padding-left:10px" href="{}">Reject</a>""".format(obj.id,url))
        else:
            return format_html("")
# Register your models here.
class LiteratureAdmin(admin.ModelAdmin):
    #这里写配置项
    list_per_page = 40
    search_fields = ('publication', 'pub_year', 'doi', 'title')  # list

    list_display = ('publication', 'pub_year', 'doi','title')  # list
    # search_fields = ('publication','title')

    def get_queryset(self, request):

        qs = super(LiteratureAdmin, self).get_queryset(request)
        return qs.order_by("publication")



admin.site.register(DataModel,DataAdmin)
admin.site.register(UserUploadModel,ReviewAdmin)

admin.site.register(LiteratureModel,LiteratureAdmin)
admin.site.site_header='PePPEr Admin System'
admin.site.site_title='PePPEr Admin System'
