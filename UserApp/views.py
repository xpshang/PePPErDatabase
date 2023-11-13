from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from UserApp.models import CustomUser as User
from django.shortcuts import render, redirect
from django.views import View

from DataApp.views import LoginRequiredView

# # 登录页面逻辑
class LoginView(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=User.objects.filter(email=username).first()
        if user is not None:
            username=user.username
        # 判断是否密码账号正确
        user = authenticate(username=username, password=password)
        if user:
            login(request,user)
            return redirect("/")
        else:
            message="该账号不存在或者密码错误"

            return render(request, 'login.html', locals())

# 注册账号
class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')
    def post(self,request):
        username = request.POST.get("username")
        email=request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password!=password2:
            message = "两次密码不一致"
            return render(request,'register.html',locals())
        user=User.objects.filter(username=username).first()
        if user is not None:
            message="该账号已经注册"
            return render(request,'register.html',locals())
        user = User.objects.filter(email = email).first()
        if user is not None:
            message = "该邮箱已经注册"
            return render(request, 'register.html', locals())

        User.objects.create_user(username,email,password)
        return redirect("/account/login")
#退出登录
class LogoutView(LoginRequiredView):
    def get(self,request):
        logout(request)
        return redirect("/account/login")
#修改密码
class ChangePasswordView(LoginRequiredView):
    def get(self,request):
        return render(request,'changepassword.html',locals())
    def post(self,request):
        old_password=request.POST.get("old_password")
        new_password=request.POST.get("new_password")
        new_password2=request.POST.get("new_password2")
        if new_password!=new_password2:
            message="两次密码不一致"
            return render(request,'changepassword.html',locals())
        user = authenticate(username=request.user.username, password=old_password)
        if not user:
            message = "旧密码输入错误"
            return render(request, 'changepassword.html', locals())
        user=User.objects.get(id=request.user.id)
        user.set_password(new_password)
        user.save()
        return redirect("/account/logout")