from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/', views.login_view, name='login_view'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^employee_dashboard/', views.index, name='employee_dashboard'),
    url(r'^$', views.index, name='index'),
]
