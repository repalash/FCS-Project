from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


# TODO palash: ... decide whether the employee is regular employee or system manager
# TODO palash: What is employees_access_user_accounts for???
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

	fields = {
		'username': request.user.username,
		'transactions': request.user.profile.transactions_set.all(),
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	# action of approve and disapprove button
	return render(request, 'approve_debit_credit_request.html', fields)


# TODO palash: ...  #redirect to user page when button is clicked
def user_accounts_list(request):
	users=[]
	fields = {
		'username': request.user.username,
		'users': users ,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}

	return render(request, 'user_accounts.html',fields)

#TODO palash: ...
def user_detail_page(request):
	transactions=[]   #transaction_id , status , amount
	fields={
		'username':request.user.username,
		'transactions':transactions,
		'has_perm_employee_operations': request.user.has_perm('BankingSystem.employee_operations'),
	}
	return render(request, 'user_detail_page.html',fields)

