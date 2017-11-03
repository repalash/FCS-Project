from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

# TODO palash: ... decide whether the employeem is regular employee or system manager
# TODO palash: ...
@login_required()
@permission_required('BankingSystem.employee_operations', raise_exception=True)
def dashboard_internal(request):
	fields = {
		'username': request.user.username,
		'has_perm_create_payments': request.user.has_perm('BankingSystem.employee_operations'),
		# Add more here
		'is_system_manager':False
	}
	return render(request, 'dashboard_internal_user.html', fields)



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

def user_accounts_list(request):
	users=[]
	fields = {
		'username': request.user.username,
		'users': users ,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}

	return render(request, 'user_accounts.html',fields)

def employees_access_user_accounts(request):
	users=[]
	fields = {
		'username': request.user.username,
		'users': users,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'employees_access_user_accounts.html',fields)

