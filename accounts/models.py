from django.db import models


class Customer(models.Model):
	email = models.EmailField(primary_key=True, max_length=100)
	name = models.CharField(max_length=100)
	balance = models.IntegerField(default=10000)
	password = models.CharField(max_length=100)

	class Meta:
		db_table = 'customer'