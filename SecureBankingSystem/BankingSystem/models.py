# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

import pyotp
from django.contrib.auth.models import User
from django.db import models
from django.db.models import SET_NULL, CASCADE

from BankingSystem.utils import BankingException


class Profile(models.Model):
	class Meta:
		permissions = (
			("user_operations", "Has permission to own an account, do account operations"),
			("create_payments", "For merchants to create payments for their users"),
			("employee_operations", "Has permissions to check the employee dashboard"),
			("view_critical_transactions", "Manager/Staff, has permission to mark critical transactions"),
			("super_perm", "For debug and superuser purposes"),
		)

	user = models.OneToOneField(User, unique=True, on_delete=CASCADE, primary_key=True)
	phone = models.CharField(max_length=13)
	address = models.CharField(max_length=200)
	totp_seed = models.CharField(max_length=16, default='0', editable=False)
	ticket_employee = models.ForeignKey("self", null=True, default=None, on_delete=SET_NULL, blank=True,
	                                    related_name="employee_ticket", editable=False)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.user.username

	def regenerate_totp_seed(self):
		self.totp_seed = pyotp.random_base32()
		self.save()
		return pyotp.totp.TOTP(self.totp_seed).provisioning_uri(str(self.user.username), issuer_name='Mortal Stanley Bank')

	def verify_otp(self, otp):
		if len(self.totp_seed) != 16:
			raise BankingException('Invalid OTP State, authenticate again.')
		totp = pyotp.TOTP(self.totp_seed)
		return totp.verify(otp)


class Account(models.Model):
	STATE = (
		('O', 'Open'),
		('C', 'Closed'),
		('S', 'Suspended'),
	)
	user = models.ForeignKey(Profile, null=True, on_delete=SET_NULL, blank=True)
	number = models.IntegerField(primary_key=True, unique=True)
	balance = models.IntegerField(default=0, editable=False)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)
	state = models.CharField(max_length=1, choices=STATE)

	def __str__(self):
		return str(self.number) + " : " + self.user.user.username + " : " + str(
			self.balance) + " : " + self.get_state_display()

	def do_debit_credit(self, transaction_type, amount, transaction, commit=True):
		if amount <= 0:
			raise BankingException('Invalid Amount')
		if transaction is None or transaction.amount != amount and transaction.status != 'A':
			raise BankingException('Security Error')
		if transaction_type == Transactions.TYPE_DEBIT:
			self.balance -= amount
		if transaction_type == Transactions.TYPE_CREDIT:
			self.balance += amount
		if self.balance < 0:
			raise BankingException('Security Error')
		if commit:
			self.save()


class Transactions(models.Model):
	TYPE_CREDIT = 0
	TYPE_DEBIT = 1
	TYPE_TRANSACTION = 2
	CRITICAL_LIMIT = 10000
	STATUS = (
		('C', "OTP_or_Payment"),
		('A', "Employee_Approval"),
		('P', "Processed"),
		('R', "Rejected"),
		('I', "Insufficient_Funds"),
		('E', "Error"),
	)
	employee = models.ForeignKey(Profile, null=True, blank=True, on_delete=SET_NULL)
	from_account = models.ForeignKey(Account, related_name="from_account", null=True, on_delete=SET_NULL, blank=True)
	to_account = models.ForeignKey(Account, related_name="to_account", null=True, on_delete=SET_NULL, blank=True)
	amount = models.IntegerField(default=0, editable=False)
	status = models.CharField(max_length=1, choices=STATUS, editable=False)
	is_cash = models.BooleanField(editable=False)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		from_account = "Cash" if not self.from_account else str(self.from_account.number)
		to_account = "Cash" if not self.to_account else str(self.to_account.number)
		return str(self.id) + " " + from_account + " " + to_account + "  " + str(
			self.amount) + " " + self.get_status_display()

	@staticmethod
	def create(transaction_type, user, from_account_no, to_account_no, amount, pref_employee=""):
		is_cash = False
		if amount <= 0:
			raise BankingException('Invalid Amount')
		if transaction_type != Transactions.TYPE_TRANSACTION:
			is_cash = True
		try:
			amount = int(amount.strip())
			if from_account_no is not None:
				from_account_no = int(from_account_no.strip())
			if to_account_no is not None:
				to_account_no = int(to_account_no.strip())
		except Exception as e:
			raise BankingException("Invalid data")
		if from_account_no is None and transaction_type == Transactions.TYPE_CREDIT:
			from_account = None
		else:
			from_account = Account.objects.filter(number=from_account_no)
			if len(from_account) == 0:
				raise BankingException('You don\'t own this account.')
			from_account = from_account[0]
			if from_account.user.user.username != user.username:
				raise BankingException('Account doesn\'t belong to you')
			if from_account.balance < amount:
				raise BankingException("Insufficient Funds")
		if to_account_no is None and transaction_type == Transactions.TYPE_DEBIT:
			to_account = None
		else:
			to_account = Account.objects.filter(number=to_account_no)
			if len(to_account) == 0:
				raise BankingException('Cannot send to this account')
			to_account = to_account[0]
		if transaction_type == Transactions.TYPE_TRANSACTION and from_account.number == to_account.number:
			raise BankingException("Cannot transfer to same account")
		group = 'Employees'
		if amount >= Transactions.CRITICAL_LIMIT:
			group = 'Staff'
		employees = User.objects.filter(groups__name=group)
		if is_cash and pref_employee and len(pref_employee) > 0:
			employees = employees.filter(username=pref_employee)
		if employees.count() == 0:
			raise BankingException('No employee available at the moment. Maybe transaction is critical. ')
		employee = employees[randint(0, employees.count() - 1)]
		if employee is None:
			raise BankingException('No employee available at the moment')
		transaction = Transactions(employee=employee.profile, from_account=from_account, to_account=to_account,
		                           amount=amount, status='C', is_cash=is_cash)
		transaction.save()
		return transaction

	def __init__(self, *args, **kwargs):
		super(Transactions, self).__init__(*args, **kwargs)

	def verify_otp(self, otp):
		account = self.from_account
		if account is None:
			account = self.to_account
		if account is None:
			raise BankingException('Invalid transaction')
		if len(account.user.totp_seed) != 16:
			self.status = 'E'
			self.save()
			raise BankingException('Re-authenticate from authenticator and make another transaction')
		if self.status != 'C':
			self.status = 'E'
			self.save()
			raise BankingException('Problem with the transaction, make another transaction')
		try:
			otp = int(otp)
		except:
			raise BankingException('Invalid OTP')
		if not account.user.verify_otp(otp):
			raise BankingException('Incorrect OTP')
		self.status = 'A'
		self.save()

	def process_transaction(self, employee=None):
		if self.status != 'A':
			raise BankingException('Problem with the transaction')
		if (self.amount >= Transactions.CRITICAL_LIMIT or self.is_cash) and (
						self.employee is None or self.employee.user.username != employee.username):
			raise BankingException('Employee didn\'t approve the transaction')
		if self.from_account is not None and self.amount > self.from_account.balance:
			self.status = 'I'
			self.save()
			raise BankingException('Insufficient Funds')
		if self.to_account.state != 'O':
			self.status = 'E'
			self.save()
			raise BankingException('Cannot transfer to this account')
		if self.from_account:
			self.from_account.do_debit_credit(Transactions.TYPE_DEBIT, self.amount, self, False)
		if self.to_account:
			self.to_account.do_debit_credit(Transactions.TYPE_CREDIT, self.amount, self, False)
		if self.from_account:
			self.from_account.save()
		if self.to_account:
			self.to_account.save()
		self.status = 'P'
		self.save()

	def payment_approve_transaction(self):
		if self.status != 'C':
			if self:
				self.status = 'E'
				self.save()
			raise BankingException('There was a problem with the transaction/OTP')
		self.status = 'A'
		self.save()
		if self.amount >= Transactions.CRITICAL_LIMIT:
			group = 'Staff'
			employees = User.objects.filter(groups__name=group)
			if employees.count() == 0:
				raise BankingException('Critical transaction: No employee available at the moment.')
			employee = employees[randint(0, employees.count() - 1)]
			if employee is None:
				raise BankingException('Critical transaction: No employee available at the moment')
			self.employee = employee.profile
			self.save()
		else:
			self.process_transaction()

	def payment_reject_transaction(self):
		if self.status != 'C':
			self.status = 'E'
			self.save()
			raise BankingException('There was a problem with the transaction')
		self.status = 'R'
		self.save()

	def reject_transaction(self, employee):
		if self.status != 'A':
			raise BankingException('Problem with the transaction')
		if self.employee is None:
			raise BankingException('This transaction cannot be rejected')
		if self.employee.user.username != employee.username:
			raise BankingException('You cannot do that')
		self.status = 'R'
		self.save()


class Payments(models.Model):
	merchant = models.ForeignKey(Profile, related_name='payment_merchant', null=True, editable=False)
	user_account = models.ForeignKey(Account, related_name='payment_user', null=True, editable=False)
	transaction = models.ForeignKey(Transactions, null=True, default=None, blank=True, editable=False)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.target_user + " -> " + self.target_account.user + " : Approved:" + (
			self.transaction is not None)

	@staticmethod
	def create(merchant, target_account_no, amount):
		try:
			amount = int(amount)
			target_account_no = int(target_account_no)
		except:
			raise BankingException('Invalid Data')
		if amount <= 0:
			raise BankingException('Invalid Amount.')
		target_account = Account.objects.get(number=target_account_no)
		if not target_account or target_account.state != 'O':
			raise BankingException('Cannot get from this account')
		if merchant.profile.account_set.all().count() < 1:
			raise BankingException('You don\'t have an account')
		transaction = Transactions(from_account=target_account, to_account=merchant.profile.account_set.all()[0],
		                           amount=amount,
		                           status='C', is_cash=False)
		transaction.save()
		payment = Payments(merchant=merchant.profile, user_account=target_account, transaction=transaction)
		payment.save()
		return payment

	def approve(self, user):
		if user is None:
			raise BankingException('Access denied')
		if self.user_account.user.user.username != user.username:
			raise BankingException('You cannot do that')
		if self.transaction is None:
			raise BankingException('There was a problem with the transaction')
		self.transaction.payment_approve_transaction()

	def reject(self, user):
		if user is None:
			raise BankingException('Access denied')
		if self.user_account.user.user.username != user.username:
			raise BankingException('You cannot do that')
		if self.transaction is None:
			raise BankingException('There was a problem with the transaction')
		self.transaction.payment_reject_transaction()
