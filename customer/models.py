from django.db import models


class Bill(models.Model):
	creator_email = models.EmailField(max_length=100)
	creator_name = models.CharField(max_length=100)

	receiver_email = models.EmailField(max_length=100)
	receiver_name = models.CharField(max_length=100)
	amount = models.IntegerField()
	product = models.CharField(max_length=100)
	due_date = models.DateField()
	created_at = models.DateTimeField()
	status = models.CharField(max_length=20, default='Pending')
	message = models.CharField(max_length=200, default='Message not available')

	class Meta:
		db_table = 'bill' 


class Notification(models.Model):
	from_email = models.EmailField(max_length=100)
	to_email = models.EmailField(max_length=100)
	created_at = models.DateTimeField()
	bill_id = models.IntegerField()

	class Meta:
		db_table = 'notification'