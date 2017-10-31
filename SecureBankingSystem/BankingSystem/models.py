# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
	user = models.ForeignKey(User, unique=True, editable=False)
	aadhar = models.CharField(max_length=30)
	phone = models.CharField(max_length=13)
	address = models.CharField(max_length=200)


class Employee(Profile):
	manager = models.ForeignKey("self", null=True)


class Account(models.Model):
	user = models.ForeignKey(Profile, editable=False)
	number = models.IntegerField(primary_key=True, unique=True, editable=False)
	balance = models.IntegerField(default=0)


class Transactions(models.Model):
	STATUS = (
		('A', "Under Approval"),
		('P', "Processed"),
		('I', "Insufficient Funds"),
		('E', "Unknown Error"),
	)
	employee = models.ForeignKey(Employee)
	from_account = models.ForeignKey(Account, related_name="from_account", null=True)
	to_account = models.ForeignKey(Account, related_name="to_account", null=True)
	amount = models.IntegerField(default=0)
	status = models.CharField(max_length=1, choices=STATUS)
	is_cash = models.BooleanField()
