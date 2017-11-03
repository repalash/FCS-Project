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
	url(r'^transaction_confirmation/<transaction_id>', user_views.transaction_confirmation,
	    name='transaction_confirmation'),
]
