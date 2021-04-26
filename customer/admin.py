from django.contrib import admin
from .models import *


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
	list_display = (
		'id','creator_email', 'creator_name', 'receiver_email', 'receiver_name',
		'amount', 'due_date', 'created_at','product','status', 'message'
		)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'from_email','to_email', 'created_at','bill_id',
		)