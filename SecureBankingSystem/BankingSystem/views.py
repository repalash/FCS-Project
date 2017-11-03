# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from BankingSystem import models
from BankingSystem.models import Transactions
from BankingSystem.utils import custom_redirect, do_get


@login_required()
def index(request):
	return HttpResponse("Hello, World")


def login_view(request):  # done
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


@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
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


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def approve_debit_credit(request):
	users = []  # contain list of users where each object has username, account number and balance
	fields = {
		'username': request.user.username,
		'users': users,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	# action of approve and disapprove button
	return render(request, 'approve_debit_credit.html', fields)


def dashboard_internal(request):
	fields = {
		'username': request.user.username,
		'has_perm_create_payments': request.user.has_perm('BankingSystem.employee_operations'),
		# Add more here
	}


def edit_user_details(request):  # done

	fields = {
		'username': request.user.username,
		'address': request.user.address,
		'name': request.user.name,
		'phone': request.user.phone,
		'error': '',
		'iserror': False,
	}
	if request.method != 'POST':
		return render(request, 'edit_user_details.html', fields)

	username = request.POST['username']
	password = request.POST['password']
	repeat_password = request.POST['repeat_password']
	name = request.POST['name']
	address = request.POST['address']
	phone = request.POST['phone']

	return render(request, 'dashboard_external_user.html')


def handle_request_technical_account_access(request):
	pass


# Transfer money from one account to another
# TODO team: show user all possible accounts that he own, check HTML file
# TODO team: receiver username not needed
# TODO team, palash: add custom employee field
# TODO palash: send OTP to user
@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
def make_transactions(request):
	fields = {
		'username': request.user.username,
		'error': '',
		'has_perm_view_critical_transactions': request.user.has_perm('BankingSystem.view_critical_transactions'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
		'accounts': request.user.profile.account_set.all()
	}
	if request.method != 'POST':
		return render(request, 'make_transactions.html', fields)
	sender_account_number = request.POST['sender_account_number']
	receiver_account_number = request.POST['receiver_account_number']
	amount = request.POST['amount']
	try:
		transaction = Transactions(Transactions.TYPE_TRANSACTION, request.user, sender_account_number,
		                           receiver_account_number, amount)
	except Exception as e:
		fields['error'] = e.message
		return render(request, 'make_transactions.html', fields)
	return redirect("transaction_confirmation", transaction_id=transaction.id)


def passbook(request):  # done

	transactions = []  # list of objects containing transaction_id , status , amount
	# need account number for getting transactions
	fields = {
		'username': request.user.username,
		'error': '',
		'transactions': transactions,
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}

	return render(request, 'passbook.html')


# account_number = request.POST['account_number']


def reenter_password(request):
	password = request.POST['password']
	fields = {
		'username': request.user.username,
		'error': '',
	}


def request_transaction_review(request):  # done
	fields = {
		'username': request.user.username,
		'is_error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}
	if request.method != 'POST':
		return render(request, 'request_transaction_review.html', fields)
	transaction_id = request.POST['transaction_id']
	preferred_employee_id = request.POST['preferred_employee_id']
	comment = request.POST['comment']

	return render(request, 'dashboard_external_user.html')


# TODO team: No need for password
# TODO palash: Implement OTP
# Get OTP from the user, verifies and sends transaction for approval
def transaction_confirmation(request, transaction_id):  # done
	fields = {
		'authentication_error': '',
		'username': request.user.username,
		'error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.view_user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}

	if request.method != 'POST':
		return render(request, 'transaction_confirmation_otp.html', fields)

	otp = request.POST['otp']
	transaction = Transactions.objects.get(pk=transaction_id)
	try:
		transaction.verify_otp(otp)
	except Exception as e:
		fields['authentication_error'] = e.message
		return render(request, 'transaction_confirmation_otp.html', fields)
	return custom_redirect("dashboard", success='Transaction sent for approval')

def passbook_account_no(request):
	return None
