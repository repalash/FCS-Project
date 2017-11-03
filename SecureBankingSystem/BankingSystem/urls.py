from django.conf.urls import url

from BankingSystem import user_views, employee_views
from . import views

urlpatterns = [
	url(r'^login/', views.login_view, name='login_view'),
	url(r'^dashboard_external/', user_views.dashboard_external, name='dashboard'),
	url(r'^employee_dashboard/', views.index, name='employee_dashboard'),
	url(r'^$', views.index, name='index'),

	# New code
	url(r'^make_transaction/', user_views.make_transactions, name='make_transaction'),
	url(r'^debit_credit/', user_views.debit_credit, name='debit_credit'),
	url(r'^approve_debit_credit/', employee_views.approve_debit_credit, name='approve_debit_credit'),
	url(r'^passbook/', user_views.passbook, name='passbook'),
	url(r'^request_transaction_review/', views.request_transaction_review, name='request_transaction_review'),
	url(r'^passbook_account_no/', views.passbook_account_no, name='passbook_account_no'),
	url(r'^edit_user_details/', user_views.edit_user_details, name='edit_user_details'),
	url(r'^transaction_confirmation/<transaction_id>', user_views.transaction_confirmation, name='transaction_confirmation'),
    url(r'^reenter_password/', user_views.reenter_password, name='reenter_password'),
	#url(r'^edit_user_details/', user_views.edit_user_details, name='edit_user_details'),

	#employess
	url(r'^user_accounts_list/', employee_views.user_accounts_list, name='user_accounts_list'),
	url(r'^approve_debit_credit/', employee_views.approve_debit_credit, name='approve_debit_credit'),
	url(r'^employees_access_user_accounts/', employee_views.employees_access_user_accounts, name='employees_access_user_accounts'),
	#url(r'^handle_request/', employee_views.handle_request, name='handle_request'),
	url(r'^create_payment/', employee_views.create_payment, name='create_payment'),
	url(r'^approve_payments_for_users/', employee_views.approve_payments_for_users, name='approve_payments_for_users'),
	url(r'^technical_accounts_access_for_users/', employee_views.technical_accounts_access_for_users, name='technical_accounts_access_for_users'),
]
