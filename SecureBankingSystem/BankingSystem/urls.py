from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/', views.login_view, name='login_view'),
    url(r'^dashboard_external/', views.dashboard_external, name='dashboard'),
    url(r'^employee_dashboard/', views.index, name='employee_dashboard'),
    url(r'^$', views.index, name='index'),

    #New code
    url(r'^make_transaction/', views.make_transaction, name='make_transaction'),
    url(r'^approve_debit_credit/', views.approve_debit_credit, name='approve_debit_credit'),
    url(r'^passbook/', views.passbook, name='passbook'),
    url(r'^request_transaction_review/', views.request_transaction_review, name='request_transaction_review'),
    url(r'^transaction_confirmation/', views.transaction_confirmation, name='transaction_confirmation'),
    url(r'^passbook_account_no/', views.passbook_account_no, name='passbook_account_no'),
    url(r'^passbook/', views.passbook, name='passbook'),
    url(r'^request_transaction_review/', views.request_transaction_review, name='request_transaction_review'),
    url(r'^edit_user_details/', views.edit_user_details, name='edit_user_details'),
]
