from django.urls import path
from . import views

urlpatterns = [
	path('', views.login, name='login'),
	path('register/', views.register, name='register'),
	path('forgot-password/', views.forgot_password, name='forgot-password'),
	path('forgot-password/<email>/', views.forgot_password, name='forgot-password-email'),
	path('logout/', views.logout, name='logout'),
]