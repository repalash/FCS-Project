# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import SET_NULL, CASCADE


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
	is_employee = models.BooleanField(default=False)
	ticket_employee = models.ForeignKey("self", null=True, default=None, on_delete=SET_NULL, blank=True)
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
	STATUS = (
		('A', "Under Approval"),
		('P', "Processed"),
		('I', "Insufficient Funds"),
		('E', "Unknown Error"),
	)
	employee = models.ForeignKey(Profile)
	from_account = models.ForeignKey(Account, related_name="from_account", null=True, on_delete=SET_NULL, blank=True)
	to_account = models.ForeignKey(Account, related_name="to_account", null=True, on_delete=SET_NULL, blank=True)
	amount = models.IntegerField(default=0)
	status = models.CharField(max_length=1, choices=STATUS)
	is_cash = models.BooleanField()
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.from_account.number) + " -> " + str(self.to_account.number) + " : " + str(
			self.amount) + " : " + self.get_status_display()


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
