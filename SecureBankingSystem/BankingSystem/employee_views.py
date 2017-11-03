from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from BankingSystem.utils import do_get, custom_redirect


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def dashboard_internal(request):
	fields = {
		'redirect_info': do_get(request.GET, 'info'),  # Like already logged in
		'redirect_success': do_get(request.GET, 'success'),  # Like login successful
		'redirect_error': do_get(request.GET, 'error'),  # Generic site error
		'error': '',
		'username': request.user.username,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'dashboard_internal_user.html', fields)


# TODO palash: ...
@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def approve_debit_credit(request):
	fields = {
		'username': request.user.username,
		'transactions': map(lambda x: str(x).split(), list(request.user.profile.transactions_set.all())),
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	# action of approve and disapprove button
	return render(request, 'approve_debit_credit_request.html', fields)


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def user_accounts_list(request):
	fields = {
		'redirect_info': do_get(request.GET, 'info'),  # Like already logged in
		'redirect_success': do_get(request.GET, 'success'),  # Like login successful
		'redirect_error': do_get(request.GET, 'error'),  # Generic site error
		'username': request.user.username,
		'users': request.user.profile.employee_ticket.all(),
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'user_account_list.html', fields)


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def user_detail_page(request, username):
	user = get_object_or_404(User, pk=username)
	if user.ticket_employee.user.username != request.user.username:
		return custom_redirect('user_account_list', error='Access denied')
	accounts = user.profile.account_set.all()
	account_transactions = []
	for i in accounts:
		account_transactions.extend(map(lambda x: str(x).split(), list(i.from_account.all())))
		account_transactions.extend(map(lambda x: str(x).split(), list(i.to_account.all())))
	fields = {
		'username': request.user.username,
		'user': user,
		'account_transactions': account_transactions,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'user_detail_page.html', fields)


def employees_access_user_accounts(request):
	users = []
	fields = {
		'username': request.user.username,
		'users': users,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'employees_access_user_accounts.html', fields)
