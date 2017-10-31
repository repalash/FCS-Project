# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import SET_NULL, CASCADE


class Profile(models.Model):
	user = models.OneToOneField(User, unique=True, editable=False, on_delete=CASCADE, primary_key=True)
	phone = models.CharField(max_length=13)
	address = models.CharField(max_length=200)
	is_employee = models.BooleanField(default=False)
	manager = models.ForeignKey("self", null=True, default=None, on_delete=SET_NULL)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)


class Account(models.Model):
	user = models.ForeignKey(Profile, editable=False, null=True, on_delete=SET_NULL)
	number = models.IntegerField(primary_key=True, unique=True, editable=False)
	balance = models.IntegerField(default=0)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)


class Transactions(models.Model):
	STATUS = (
		('A', "Under Approval"),
		('P', "Processed"),
		('I', "Insufficient Funds"),
		('E', "Unknown Error"),
	)
	employee = models.ForeignKey(Profile)
	from_account = models.ForeignKey(Account, related_name="from_account", null=True, on_delete=SET_NULL)
	to_account = models.ForeignKey(Account, related_name="to_account", null=True, on_delete=SET_NULL)
	amount = models.IntegerField(default=0)
	status = models.CharField(max_length=1, choices=STATUS)
	is_cash = models.BooleanField()
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)


class Payments(models.Model):
	target_account = models.ForeignKey(Account)
	target_user = models.ForeignKey(Profile)
	transaction = models.ForeignKey(Transactions, null=True, default=None)
	creation_time = models.DateTimeField(auto_now_add=True)
	last_changed_time = models.DateTimeField(auto_now=True)
	is_done = models.BooleanField(default=False)

