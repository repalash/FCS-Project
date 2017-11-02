# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from BankingSystem.utils import custom_redirect, do_get


@login_required()
def index(request):
	return custom_redirect("dashboard")


def login_view(request):
	if request.user.is_authenticated:
		return custom_redirect("dashboard", info='Already logged in.')
	fields = {
		'authentication_error': ''
	}
	if request.method != 'POST':
		return render(request, 'login.html', fields)
	username = do_get(request.POST, 'username')
	password = do_get(request.POST, 'password')
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return custom_redirect("dashboard", success='Successfully logged in.')
	else:
		fields['authentication_error'] = 'Invalid username/password'
	return render(request, 'login.html', fields)


@login_required(login_url='login_view')
def dashboard_external(request):  # External user dashboard - Changed name
	fields = {
		'username': request.user.username,
		'redirect_info': do_get(request.GET, 'info'),  # Like already logged in
		'redirect_success': do_get(request.GET, 'success'),  # Like login successful
		'redirect_error': do_get(request.GET, 'error'),  # Generic site error
		'error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),  # check if user is Company
		# Add more here
	}

	return render(request, 'dashboard_external_user.html', fields)


def approve_debit_credit(request):
	users = []  # contain list of users where each object has username, account number and balance
	fields = {
		'username': request.user.username,
		'users': users,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	# action of approve and disapprove button
	return




def dashboard_internal(request):
	fields = {
		'username': request.user.username,
		'has_perm_create_payments': request.user.has_perm('BankingSystem.employee_operations'),
		# Add more here
	}


def edit_user_details(request):
	username = request.POST['username']
	password = request.POST['password']
	repeat_password = request.POST['repeat_password']
	name = request.POST['name']
	address = request.POST['address']
	phone = request.POST['phone']

	fields = {
		'username': request.user.username,
		'address': request.user.address,
		'name': request.user.name,
		'phone': request.user.phone,
		'error': '',
	}


def handle_request_technical_account_access(request):
	pass


def make_transaction(request):
	sender_account_number = request.POST['sender_account_number']
	reciever_username = request.POST['reciever_username']
	reciever_account_number = request.POST['reciever_account_number']
	amount = request.POST['amount']

	fields = {
		'username': request.user.username,
		'error': '',
		'has_perm_view_critical_transactions': request.user.has_perm('BankingSystem.view_critical_transactions'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}
	return custom_redirect("transaction_confirmation", success='Confirm your transaction.')


def passbook(request):
	fields = {
		'username': request.user.username,
		'error': '',
		# 'amount': ?????
	}
	account_number = request.POST['account_number']


def reenter_password(request):
	password = request.POST['password']
	fields = {
		'username': request.user.username,
		'error': '',
	}


def request_transaction_review(request):
	fields = {
		'username': request.user.username,
		'error': '',
	}
	transaction_id = request.POST['transaction_id']
	preferred_employee_id = request.POST['preferred_employee_id']
	comment = request.POST['comment']


def transaction_confirmation(request):
	# otp is not authenticated

	fields = {
		'authentication_error':'',
		'username': request.user.username,
		'error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.view_user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}
	password = request.POST['password']
	username= request.user.username
	otp = request.POST['otp']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		return custom_redirect("dashboard", success='Successfully transaction.')
	else:
		fields['authentication_error'] = 'Invalid username/password'


def passbook_account_number(request):
	fields = {
		'iserror':False,
		'error':'',
	}
	account_number = request.POST["account_numbar"]

	context = {
		'account_number':account_number,
	}
	return render(request,'passbook.html',context)


def passbook_account_no(request):
	return None