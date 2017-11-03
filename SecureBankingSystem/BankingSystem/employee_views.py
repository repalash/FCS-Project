from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


# TODO palash: ...
@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def dashboard_internal(request):
	fields = {
		'username': request.user.username,
		'has_perm_create_payments': request.user.has_perm('BankingSystem.employee_operations'),
		# Add more here
	}


# TODO palash: ...
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
	return render(request, 'approve_debit_credit_request.html', fields)
