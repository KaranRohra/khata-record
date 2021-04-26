from django.urls import path
from . import views

urlpatterns = [
	path('home/', views.home, name='home'),
	path('create-bill/', views.create_bill, name='create-bill'),
	path('edit-bill/<bid>/', views.edit_bill, name='edit-bill'),
	path('delete-bill/<bid>/', views.delete_bill, name='delete-bill'),
	path('received-bill/', views.received_bill, name='received-bills'),
	path('bill-details/<int:bid>/', views.view_bill_details, name='view-bill-details'),
	path('notifications/', views.notifications, name='notifications'),
	path('profile/', views.profile, name='profile')
]