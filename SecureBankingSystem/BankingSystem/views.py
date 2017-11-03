# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from BankingSystem.utils import custom_redirect, do_get


@login_required()
def index(request):
	return redirect("login_view")


def login_view(request):
	if request.user.is_authenticated:
		if request.user.has_perm('BankingSystem.user_operations'):
			return custom_redirect("dashboard", success='Already logged in.')
		if request.user.has_perm('BankingSystem.employee_operations'):
			return custom_redirect("employee_dashboard", success='Already logged in.')
		return redirect("index")

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
		if user.has_perm('BankingSystem.user_operations'):
			return custom_redirect("dashboard", success='Successfully logged in.')
		if user.has_perm('BankingSystem.employee_operations'):
			return custom_redirect("employee_dashboard", success='Successfully logged in.')
		return redirect('index')
	else:
		fields['authentication_error'] = 'Invalid username/password'
	return render(request, 'login.html', fields)


def handle_request_technical_account_access(request):
	pass


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


def passbook_account_no(request):
	return None


@login_required()
def logout_view(request):
	logout(request)
	return redirect('login_view')
