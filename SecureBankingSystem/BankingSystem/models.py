# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

from django.contrib.auth.models import User
from django.db import models
from django.db.models import SET_NULL, CASCADE

from BankingSystem.utils import BankingParseException


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


class Transactions(models.Model):
	TYPE_CREDIT = 0
	TYPE_DEBIT = 1
	TYPE_TRANSACTION = 2
	CRITICAL_LIMIT = 10000
	STATUS = (
		('C', "Created"),
		('A', "Under_Approval"),
		('P', "Processed"),
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
		from_account = "Cash" if self.from_account else str(self.from_account.number)
		to_account = "Cash" if self.to_account else str(self.to_account.number)
		return str(self.id) + " " + from_account + " " + to_account + "  " + str(
			self.amount) + " " + self.get_status_display()

	@staticmethod
	def create(transaction_type, user, from_account_no, to_account_no, amount):
		is_cash = False
		if transaction_type != Transactions.TYPE_TRANSACTION:
			is_cash = True
		if from_account_no is None and transaction_type == Transactions.TYPE_CREDIT:
			from_account = None
		else:
			try:
				amount = int(amount)
			except:
				raise BankingParseException("Invalid Amount")
			from_account = Account.objects.filter(number=from_account_no)
			if len(from_account) == 0:
				raise BankingParseException('You don\'t own this account.')
			from_account = from_account[0]
			if from_account.user.user.username != user.username:
				raise BankingParseException('Account doesn\'t belong to you')
			if from_account.balance < amount:
				raise BankingParseException("Insufficient Funds")
		if to_account_no is None and transaction_type == Transactions.TYPE_DEBIT:
			to_account = None
		else:
			to_account = Account.objects.filter(number=to_account_no)
			if len(to_account) == 0:
				raise BankingParseException('Cannot send to this account')
			to_account = to_account[0]
		if transaction_type == Transactions.TYPE_TRANSACTION and from_account.number == to_account.number:
			raise BankingParseException("Cannot transfer to same account")
		group = 'Employee'
		if amount >= Transactions.CRITICAL_LIMIT:
			group = 'Staff'
		employees = User.objects.filter(groups__name=group)
		if employees.count() == 0:
			raise BankingParseException('No employee available at the moment')
		employee = employees[randint(0, employees.count() - 1)]
		if employee is None:
			raise BankingParseException('No employee available at the moment')
		verification_otp = 4321  # TODO palash: randint(999, 10000)
		return Transactions(employee=employee, from_account=from_account, to_account=to_account, amount=amount,
		                    status='C', is_cash=is_cash, verification_otp=verification_otp)

	def __init__(self, *args, **kwargs):
		super(Transactions, self).__init__(*args, **kwargs)

	def verify_otp(self, otp):
		if self.verification_otp == 0:
			raise BankingParseException('Expired OTP')
		if self.verification_otp != otp:
			raise BankingParseException('Incorrect OTP')
		self.status = 'A'
		self.verification_otp = 0
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
