from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from BankingSystem.models import Transactions
from BankingSystem.utils import do_get, custom_redirect, BankingParseException


# External user dashboard
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
    }

    return render(request, 'dashboard_external_user.html', fields)


# Transfer money from one account to another
# TODO team: show user all possible accounts that he own, check HTML file - Done. Now allows user to select from a dropdown.
# TODO team: receiver username not needed - Done. Removed from page
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
        transaction = Transactions.create(Transactions.TYPE_TRANSACTION, request.user, sender_account_number,
                                          receiver_account_number, amount)
    except BankingParseException as e:
        fields['error'] = e.message
        return render(request, 'make_transactions.html', fields)
    return redirect("transaction_confirmation", transaction_id=transaction.id)


# Get OTP from the user, verifies and sends transaction for approval
# TODO team: No need for password - Done. Removed from the page
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

    otp = request.POST['otp']
    transaction = Transactions.objects.get(pk=transaction_id)
    try:
        transaction.verify_otp(otp)
    except BankingParseException as e:
        fields['authentication_error'] = e.message
        return render(request, 'transaction_confirmation_otp.html', fields)
    return custom_redirect("dashboard", success='Transaction sent for approval')


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

    username = request.POST['username']
    password = request.POST['password']
    repeat_password = request.POST['repeat_password']
    name = request.POST['name']
    address = request.POST['address']
    phone = request.POST['phone']

    return render(request, 'dashboard_external_user.html')


# Show complete transaction history
# TODO team: check HTML, not in format - Done.
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


# TODO team, palash: Make html, fields with employee ID page and redirect to transaction confirmation OTP page.
# Page created
def debit_credit(request):
    fields = {
        'accounts': request.user.profile.account_set.all(),
        'username': request.user.username,
        'error': '',
    }
    if request.method != 'POST':
        return render(request, 'debit_credit.html', fields)

    account = do_get(request.POST, 'account')
    type = do_get(request.POST, 'debit_or_credit')  # Whether Debit or Credit transaction
    preferred_employee = do_get(request.POST, 'preferred_employee')
    amount = do_get(request.POST, 'amount')
    try:
        if (type == "debit"):
            transaction = Transactions.create(Transactions.TYPE_DEBIT, request.user, None,
                                              account, amount)
        elif (type == "credit"):
            transaction = Transactions.create(Transactions.TYPE_CREDIT, request.user, account,
                                              None, amount)
        else:  # can this happen?
            abc = None

    except BankingParseException as e:
        fields['error'] = e.message
        return render(request, 'debit_credit.html', fields)
    return redirect("transaction_confirmation", transaction_id=transaction.id)
