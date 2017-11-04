from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from BankingSystem.models import Transactions
from BankingSystem.utils import do_get, custom_redirect, BankingException


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


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def approve_transaction_employee(request):
	fields = {
		'redirect_info': do_get(request.GET, 'info'),  # Like already logged in
		'redirect_success': do_get(request.GET, 'success'),  # Like login successful
		'redirect_error': do_get(request.GET, 'error'),  # Generic site error
		'username': request.user.username,
		'transactions': map(lambda x: str(x).split(), list(request.user.profile.transactions_set.all())),
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'approve_transaction_employee.html', fields)


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def approve_transaction_id(request, transaction_id):
	transaction = get_object_or_404(Transactions, pk=transaction_id)
	try:
		if transaction.employee.user.id != request.user.id:
			return custom_redirect('approve_transaction_employee', success="You don't have permission")
		transaction.process_transaction(request.user)
		if transaction.status == 'P':
			return custom_redirect('approve_transaction_employee', success="Transaction processed")
	except Exception as e:
		return custom_redirect('approve_transaction_employee', error=e.message)
	return custom_redirect('approve_transaction_employee', error="Unknown error")


@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def reject_transaction_id(request, transaction_id):
	transaction = get_object_or_404(Transactions, pk=transaction_id)
	try:
		if transaction.employee.user.username != request.user.username:
			return custom_redirect('approve_transaction_employee', success="You don't have permission")
		transaction.reject_transaction(request.user)
		if transaction.status == 'R':
			return custom_redirect('approve_transaction_employee', success="Transaction rejected")
	except Exception as e:
		return custom_redirect('approve_transaction_employee', error=e.message)
	return custom_redirect('approve_transaction_employee', error="Unknown error")


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
	user = get_object_or_404(User, username=username)
	if user.profile.ticket_employee is None or user.profile.ticket_employee.user.username != request.user.username:
		return custom_redirect('user_accounts_list', error='Access denied')
	accounts = user.profile.account_set.all()
	account_transactions = []
	for i in accounts:
		account_transactions.extend(map(lambda x: str(x).split(), list(i.from_account.all())))
		account_transactions.extend(map(lambda x: str(x).split(), list(i.to_account.all())))
	account_transactions.sort(cmp=lambda x, y: int(y[0]) - int(x[0]))
	fields = {
		'username': request.user.username,
		'user': user,
		'account_transactions': account_transactions,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'user_detail_page.html', fields)


#TODO team: What's this?? - Employees get the list of user requests to troubleshoot (technical account access)
def employees_access_user_accounts(request):
	users = []
	fields = {
		'username': request.user.username,
		'users': users,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'employees_access_user_accounts.html', fields)
