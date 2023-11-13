from django.http import HttpResponse, JsonResponse

from DataApp.views import addDataNow


class Custom403Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 403 and request.path.startswith("/admin/upload/"):
            # 处理403错误逻辑，比如重定向到登录页面或显示自定义错误消息
            return addDataNow(request)
        return response