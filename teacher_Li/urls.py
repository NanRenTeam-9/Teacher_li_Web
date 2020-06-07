"""teacher_Li URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from main_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page),
    path('yq/', views.main_page2),   # 疫情界面
    path('c1/', views.get_c1_data),  # 正中间模块c1数据
    path('c2/', views.get_c2_data),  # c2模块 数据
    path('l1/', views.get_l1_data),  # 左边第一个l1数据
    path('l2/', views.get_l2_data),  # 左边第二个模块l2数据
    path('r1/', views.get_r1_data),  # 右边第一个r1数据
    path('r2/', views.get_r2_data),  # 右边第二个r2数据
    path('time/', views.get_time),   # 时间数据
]
