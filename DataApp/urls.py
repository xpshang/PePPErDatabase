"""pepperdatabase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from DataApp.views import DownloadDataView, DataPlotterView, ExportDataView, UploadView, \
    ToolView, FinderView, DataPlotFieldListView, AdminReviewView, ReviewSubmitView, HistoryView, get_image, \
    AdminUploadView, UploadListView
from DataApp.views import HomeView
urlpatterns = [
    # path('admin/', admin.site.urls),
    path("download/", DownloadDataView.as_view()),
    path("data/plotter/plot/", DataPlotterView.as_view()),
    path("data/plotter/fileds/", DataPlotFieldListView.as_view()),
    path("export/", ExportDataView.as_view()),
    path("data/upload/", UploadView.as_view()),
    path("admin/upload/", AdminUploadView.as_view()),
    path("tool/", ToolView.as_view()),
    path("finder/", FinderView.as_view()),
    path("review/", AdminReviewView.as_view()),
    path("reviewsubmit/", ReviewSubmitView.as_view()),
    path("history/", HistoryView.as_view()),
    path("upload/history", UploadListView.as_view()),
    path("img/download/", get_image),
    path("", HomeView.as_view())
]
