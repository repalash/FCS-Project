from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from BankingSystem.models import Transactions
from BankingSystem.utils import do_get, custom_redirect, BankingException


# External user dashboard
# TODO team: fix HTML for accounts list in HTML
@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
def dashboard_external(request):
	fields = {
		'username': request.user.username,
		'redirect_info': do_get(request.GET, 'info'),  # Like already logged in
		'redirect_success': do_get(request.GET, 'success'),  # Like login successful
		'redirect_error': do_get(request.GET, 'error'),  # Generic site error
		'error': '',
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),  # check if user is Company
		'accounts': request.user.profile.account_set.all()
	}

	return render(request, 'dashboard_external_user.html', fields)


# Transfer money from one account to another
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
	sender_account_number = do_get(request.POST, 'sender_account_number')
	receiver_account_number = do_get(request.POST, 'receiver_account_number')
	amount = do_get(request.POST, 'amount')
	try:
		transaction = Transactions.create(Transactions.TYPE_TRANSACTION, request.user, sender_account_number,
		                                  receiver_account_number, amount)
	except BankingException as e:
		fields['error'] = e.message
		return render(request, 'make_transactions.html', fields)
	return redirect("transaction_confirmation", transaction_id=transaction.id)


# Get OTP from the user, verifies and sends transaction for approval
# TODO palash: Implement OTP
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

	otp = do_get(request.POST, 'otp')
	transaction = Transactions.objects.get(pk=transaction_id)
	info_string = 'Transaction sent for approval'
	try:
		transaction.verify_otp(otp)
		if not transaction.is_cash or transaction.amount < Transactions.CRITICAL_LIMIT:
			transaction.process_transaction()
			info_string = 'Successfully processed transaction'
	except BankingException as e:
		fields['authentication_error'] = e.message
		return render(request, 'transaction_confirmation_otp.html', fields)
	return custom_redirect("dashboard", success=info_string)


# TODO palash: ...
@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
def edit_user_details(request):
	fields = {
		'username': request.user.username,
		'address': request.user.address,
		'name': request.user.name,
		'phone': request.user.phone,
		'error': '',
		'is_error': False,
	}
	if request.method != 'POST':
		return render(request, 'edit_user_details.html', fields)

	username = do_get(request.POST, 'username')
	password = request.do_get(request.POST, 'password')
	repeat_password = do_get(request.POST, 'repeat_password')
	name = do_get(request.POST, 'name')
	address = do_get(request.POST, 'address')
	phone = do_get(request.POST, 'phone')

	return render(request, 'dashboard_external_user.html')


# Show complete transaction history
@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
def passbook(request):  # done
	accounts = request.user.profile.account_set.all()
	account_transactions = []
	for i in accounts:
		account_transactions.extend(map(lambda x: str(x).split(), list(i.from_account.all())))
		account_transactions.extend(map(lambda x: str(x).split(), list(i.to_account.all())))

	# list of objects containing transaction_id , status , amount
	# need account number for getting transactions
	fields = {
		'username': request.user.username,
		'error': '',
		'account_transactions': account_transactions,
		'has_perm_user_operations': request.user.has_perm('BankingSystem.user_operations'),
		'has_perm_create_payments': request.user.has_perm('BankingSystem.create_payments'),
	}

	return render(request, 'passbook.html')


# Doing transaction for cash transactions
@login_required()
@permission_required('BankingSystem.user_operations', raise_exception=True)
def debit_credit(request):
	fields = {
		'accounts': request.user.profile.account_set.all(),
		'username': request.user.username,
		'error': '',
	}
	if request.method != 'POST':
		return render(request, 'debit_credit.html', fields)

	account = do_get(request.POST, 'account')
	transaction_type = do_get(request.POST, 'debit_or_credit')  # Whether Debit or Credit transaction
	pref_employee = do_get(request.POST, 'preferred_employee')
	amount = do_get(request.POST, 'amount')
	try:
		if transaction_type == "debit":
			transaction = Transactions.create(Transactions.TYPE_DEBIT, request.user, account, None, amount,
			                                  pref_employee)
		elif transaction_type == "credit":
			transaction = Transactions.create(Transactions.TYPE_CREDIT, request.user, None, account, amount,
			                                  pref_employee)
		else:
			raise BankingException('Invalid request')
	except BankingException as e:
		fields['error'] = e.message
		return render(request, 'debit_credit.html', fields)
	return redirect("transaction_confirmation", transaction_id=transaction.id)
