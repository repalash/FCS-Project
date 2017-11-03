from django.conf.urls import url

from BankingSystem import user_views, employee_views
from . import views

urlpatterns = [
	url(r'^login/', views.login_view, name='login_view'),
	url(r'^logout/', views.logout_view, name='logout_view'),
	url(r'^dashboard_external/', user_views.dashboard_external, name='dashboard'),
	url(r'^employee_dashboard/', employee_views.dashboard_internal, name='employee_dashboard'),
	url(r'^$', views.index, name='index'),

	url(r'^make_transaction/', user_views.make_transactions, name='make_transaction'),
	url(r'^debit_credit/', user_views.debit_credit, name='debit_credit'),
	url(r'^approve_transaction_employee/', employee_views.approve_transaction_employee,
	    name='approve_transaction_employee'),
	url(r'^passbook/', user_views.passbook, name='passbook'),
	url(r'^request_transaction_review/', views.request_transaction_review, name='request_transaction_review'),
	url(r'^passbook_account_no/', views.passbook_account_no, name='passbook_account_no'),
	url(r'^edit_user_details/', user_views.edit_user_details, name='edit_user_details'),
	url(r'^transaction_confirmation/(?P<transaction_id>[0-9]+)', user_views.transaction_confirmation,
	    name='transaction_confirmation'),
	url(r'^reenter_password/', user_views.reenter_password, name='reenter_password'),
	url(r'^create_payment/', user_views.create_payment, name='create_payment'),
	url(r'^user_payments/', user_views.approve_payments_for_users, name='user_payments'),
	url(r'^approve_payment/(?P<payment_id>[0-9]+)', user_views.approve_payment_id, name='user_payments_approve'),
	url(r'^reject_payment/(?P<payment_id>[0-9]+)', user_views.reject_payment_id, name='user_payments_reject'),
	url(r'^technical_accounts_access/', user_views.technical_accounts_access,
	    name='technical_accounts_access'),

	url(r'^user_accounts_list/', employee_views.user_accounts_list, name='user_accounts_list'),
	url(r'^approve_transaction_employee/', employee_views.approve_transaction_employee,
	    name='approve_transaction_employee'),
	url(r'^approve_transaction/(?P<transaction_id>[0-9]+)', employee_views.approve_transaction_id,
	    name='approve_transaction_id'),
	url(r'^reject_transaction/(?P<transaction_id>[0-9]+)', employee_views.reject_transaction_id,
	    name='reject_transaction_id'),
	url(r'^employees_access_user_accounts/', employee_views.employees_access_user_accounts,
	    name='employees_access_user_accounts'),
	url(r'^user_detail_page/(?P<username>[A-Za-z0-9]+)', employee_views.user_detail_page, name='user_detail_page'),
]
