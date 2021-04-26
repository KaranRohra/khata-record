from django.shortcuts import render, redirect
from .models import Customer
from .public import send_email
from hashlib import sha256
from random import randint
from django.views.decorators.cache import cache_control


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
	if 'email' in request.session:
		return redirect('home')
	logout(request)

	template_name = 'accounts/login.html'
	if request.method == 'POST':
		status = can_login(request,request.POST)
		if status==True:
			request.session.set_expiry(0)
			if 'remember_me' in request.POST:
				request.session.set_expiry(60*60*24*30)
			return redirect('home')
		else:
			return render(request, template_name, {'error_message': status})
	else:
		return render(request, template_name)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register(request):
	if 'email' in request.session:
		return redirect('home')

	template_name = 'accounts/register.html'
	if request.method == 'POST':
		status = can_register(request.POST)
		if status==True:
			return redirect('login')
		else:
			return render(request, template_name, {'error_message':status})
	else:
		return render(request, template_name)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forgot_password(request, email=None):
	if 'email' in request.session:
		return redirect('home')

	template_name = 'accounts/forgot_password.html'

	if request.method == 'POST':
		template_name = 'accounts/change_password.html'

		if can_forgot(request.POST, request.session['otp'], email):
			return redirect('login')
		else:
			return render(request, template_name, {'error_message':'Wrong OTP or Password does not match'})

	elif 'otp' in request.session:
		return render(request, 'accounts/change_password.html')
	
	elif 'email' in request.GET:
		customer =  tuple(Customer.objects.filter(email=request.GET['email']))
		if customer:
			otp = generate_otp()
			if send_email(request.GET['email'], otp):
				request.session['otp'] = otp
				request.session.set_expiry(0)
				return redirect(f'/forgot-password/{request.GET["email"]}/')
			else:
				return render(request, template_name, {'error_message':'Failed while sending email'})
		else:
			return render(request, template_name, {'error_message':'Account with this email does not exist'})
	return render(request, template_name)


def logout(request):
	request.session.flush()
	request.session.clear_expired()
	return redirect('login')


def can_login(request, customer_data):
	email = customer_data['email']
	password = sha256(customer_data['password'].encode())
	customer = tuple(Customer.objects.filter(email=email))
	if customer:
		if customer[0].password ==  password.hexdigest():
			request.session['email'] = email
			request.session['name'] = customer[0].name
			request.session['balance'] = customer[0].balance
			return True
		return "Wrong Password"
	return "Account does not exist"


def can_register(customer_data):
	email = customer_data['email']
	customer = tuple(Customer.objects.filter(email=email))
	if not customer:
		if customer_data['password']==customer_data['confirm_password']:
			Customer(
				email=email,
				name=customer_data['name'],
				password=sha256(customer_data['password'].encode()).hexdigest()
			).save()
			return True
		return "Password not matched"
	return "Account already exist"


def generate_otp():
	otp = randint(1, 10)
	for _ in range(5):
		otp = otp*10 + randint(0, 10)
	return otp


def can_forgot(customer_data, otp, email):
	if int(customer_data['otp'])==otp and customer_data['password']==customer_data['confirm_password']:
		customer = Customer.objects.get(email=email)
		customer.password=sha256(customer_data['password'].encode()).hexdigest()
		customer.save()
		return True
	return False












