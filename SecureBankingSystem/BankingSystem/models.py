# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

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
	ticket_employee = models.ForeignKey("self", null=True, default=None, on_delete=SET_NULL, blank=True,
	                                    related_name="employee_ticket")
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.user.username


class Account(models.Model):
	STATE = (
		('O', 'Open'),
		('C', 'Closed'),
		('S', 'Suspended'),
	)
	user = models.ForeignKey(Profile, null=True, on_delete=SET_NULL, blank=True)
	number = models.IntegerField(primary_key=True, unique=True)
	balance = models.IntegerField(default=0)
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
		('C', "Created"),
		('A', "Under_Approval"),
		('P', "Processed"),
		('R', "Rejected"),
		('I', "Insufficient_Funds"),
		('E', "Error"),
	)
	employee = models.ForeignKey(Profile, null=True, blank=True, on_delete=SET_NULL)
	from_account = models.ForeignKey(Account, related_name="from_account", null=True, on_delete=SET_NULL, blank=True)
	to_account = models.ForeignKey(Account, related_name="to_account", null=True, on_delete=SET_NULL, blank=True)
	amount = models.IntegerField(default=0)
	status = models.CharField(max_length=1, choices=STATUS)
	is_cash = models.BooleanField()
	verification_otp = models.IntegerField()
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
			if from_account_no:
				from_account_no = int(from_account_no.strip())
			if to_account_no:
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
			raise BankingException('No employee available at the moment.')
		employee = employees[randint(0, employees.count() - 1)]
		if employee is None:
			raise BankingException('No employee available at the moment')
		verification_otp = 4321  # TODO palash: randint(999, 10000)
		transaction = Transactions(employee=employee.profile, from_account=from_account, to_account=to_account,
		                           amount=amount, status='C', is_cash=is_cash, verification_otp=verification_otp)
		transaction.save()
		return transaction

	def __init__(self, *args, **kwargs):
		super(Transactions, self).__init__(*args, **kwargs)

	def verify_otp(self, otp):
		if self.verification_otp == 0:
			self.status = 'E'
			self.save()
			raise BankingException('Expired OTP, make another transaction')
		if self.status != 'C':
			self.status = 'E'
			self.save()
			raise BankingException('Problem with the transaction, make another transaction')
		try:
			otp = int(otp)
		except:
			raise BankingException('Invalid OTP')
		if self.verification_otp != otp:
			raise BankingException('Incorrect OTP')
		self.status = 'A'
		self.verification_otp = 0
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


class Payments(models.Model):
	target_account = models.ForeignKey(Account)
	target_user = models.ForeignKey(Profile)
	transaction = models.ForeignKey(Transactions, null=True, default=None, blank=True)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)
	is_done = models.BooleanField(default=False)

	def __str__(self):
		return self.target_user + " -> " + self.target_account.user + " : Approved:" + (
			self.transaction is not None) + " : isDone:" + self.is_done
