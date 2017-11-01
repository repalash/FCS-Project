# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from BankingSystem.utils import custom_redirect


@login_required()
def index(request):
	return HttpResponse("Hello, World")


def login_view(request):
	if request.user.is_authenticated:
		return custom_redirect("dashboard", info='Already logged in.')
	fields = {
		'authentication_error': ''
	}
	if request.method != 'POST':
		return render(request, 'login.html', fields)
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return custom_redirect("dashboard", success='Successfully logged in.')
	else:
		fields['authentication_error'] = 'Invalid username/password'
	return render(request, 'login.html', fields)


@login_required()
def dashboard(request):  # External user dashboard
	fields = {
		'username': request.user.username,
		'redirect_info': request.GET['info'],  # Like already logged in
		'redirect_success': request.GET['success'],  # Like login successful
		'redirect_error': request.GET['error'],  # Generic site error
		'error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
		# Add more here
	}

	return render(request, 'dashboard.html', fields)