"""openai_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import os
from django.contrib import admin
from django.urls import path, include
from base_app.views import query_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", query_view, name="query"),
]

admin.site.site_header = "ChatPR Database"
admin.site.site_title = "ChatPR"
admin.site.index_title = "Members Only"
# admin.site.site_url = os.environ["CHATPR_SITE_URL"]
