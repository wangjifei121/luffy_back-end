"""luffy_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from API.views.coursedetail import CourseDetail
from API.views.courselist import Courselist
from API.views.login import LoginView
from API.views.shoppingcar import ShoppingCar
from API.views.account import AccountView
from rest_framework import routers
from API.views import text

router = routers.DefaultRouter()
router.register("courselist", Courselist)
router.register("course_detail", CourseDetail)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^login/$', LoginView.as_view()),
    url(r"shoppingcar/$", ShoppingCar.as_view({"post": "create", "get": "list"})),
    url(r"shoppingcar/(?P<course_id>\d+)/$", ShoppingCar.as_view({"put": "update", "delete": "destroy"})),
    # 结算路由
    url(r"account/$", AccountView.as_view({"post": "create", "get": "list"})),

    # text
    url(r'^page1/', text.page1),
    url(r'^page2/', text.page2),
]
