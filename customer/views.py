from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from django.utils import timezone

from datetime import date
from hashlib import sha256

from .models import *
from accounts.models import Customer


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
	if 'email' not in request.session:
		return redirect('login')

	template_name = 'customer/home.html'
	update_bill_status_according_to_time()
	context = {
		'bills':get_organised_bills(request.GET, request.session['email']),
		'last':request.GET,
		'delete_status': 'Bill Delete Successfully' if 's' in request.GET else '',
		'balance': request.session['balance'],
		'name': request.session['name'],
	}

	return render(request, template_name, context)


def get_organised_bills(context, email):
	if context and 's' not in context:
		filters = []
		if 'paid' in context:
			filters.append('"Paid"')
		if 'rejected' in context:
			filters.append('"Rejected"')
		if 'pending' in context:
			filters.append('"Pending"')
		if 'expired' in context:
			filters.append('"Expired"')

		bills = Bill.objects.raw(
			f"""
			SELECT * FROM BILL 
			WHERE CREATOR_EMAIL = '{email}' AND RECEIVER_NAME LIKE '{context['search']}%' 
			{"AND STATUS IN ("+",".join(filters)+")" if filters else ''}
			{"ORDER BY "+context['sort'] if 'sort' in context else ''}
			""")
		return bills

	return Bill.objects.filter(creator_email=email).order_by('-created_at')


def update_bill_status_according_to_time():
	cursor = Bill.objects.raw(f"""
		UPDATE BILL 
		SET STATUS = 'Expired'
		WHERE DUE_DATE < '{str(timezone.now().strftime("%Y-%m-%d"))}'
		""")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile(request):
	if 'email' not in request.session:
		return redirect('login')
	template_name = 'customer/profile.html'

	customer = Customer.objects.get(email=request.session['email'])
	context = {
		'customer': customer
	}

	if request.method == 'POST':
		status = update_profile(request.POST, customer)
		if status==True:
			return redirect('/customer/profile/?p')
		context['error_message'] = status
	if 'p' in request.GET:
		context['status'] = 'Profile Update Successfully'
	return render(request, template_name, context)


def update_profile(customer_update, customer):
	if customer_update['password'] and customer_update['confirm_password'] and customer_update['new_password']:
		if customer_update['confirm_password']!=customer_update['new_password']:
			return "Confirm password does not matched"
		if get_sha256(customer_update['password']) != customer.password:
			return "Old password does not matched"
		customer.password = get_sha256(customer_update['confirm_password'])

	customer.name = customer_update['name']
	customer.save()
	return True


def get_sha256(string):
	return sha256(string.encode()).hexdigest()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_bill(request):
	if 'email' not in request.session:
		return redirect('login')

	template_name ='customer/create_bill.html'
	if request.method == 'POST':
		status = save_bill(request, request.POST)
		if status == True:
			request.session['status'] = 'Bill Created Successfully'
			return redirect('create-bill')
		context = {
			'bill': request.POST,
			'error_message':status if status else 'Enter valid date',
		}
		return render(request, template_name, context)

	elif 'status' in request.session:
		status = request.session['status']
		del request.session['status']
		return render(request, template_name, {'status': status})

	return render(request, template_name)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def received_bill(request):
	if 'email' not in request.session:
		return redirect('login')

	template_name = 'customer/view_received_bill.html'

	received_bills = tuple(Bill.objects.filter(receiver_email=request.session['email']).order_by('-created_at'))

	if received_bills:
		return render(request, template_name, {
				'bills': zip([i for i in range(1, len(received_bills)+1)],received_bills)
			})
	return render(request, template_name, {'status': 'No Received Bills Available'})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_bill_details(request, bid):
	if 'email' not in request.session:
		return redirect('login')

	template_name = 'customer/view_bill.html'
	bill = Bill.objects.filter(pk=bid)
	
	if bill:
		bill = tuple(bill)[0]
	else:
		return redirect('home')

	if bill.receiver_email != request.session['email'] and bill.creator_email!=request.session['email']:
		return redirect('home')

	if request.method == 'POST':
		customer = Customer.objects.get(email=request.session['email'])
		if sha256(request.POST['password'].encode()).hexdigest() == customer.password:
			if 'pay' in request.POST:
				if customer.balance >= bill.amount:
					customer.balance -= bill.amount
					bill.message = request.POST['message']
					bill.status = 'Paid'
					
					bill_creator = Customer.objects.get(email=bill.creator_email)
					bill_creator.balance += bill.amount

					bill.save()
					bill_creator.save()
					customer.save()

					send_notification(request.session['email'], bill.creator_email, bid)
					return redirect(f'/customer/bill-details/{bid}/')
				return render(request, template_name, {'bill':bill,'error_message':'Insufficient Balance'})
			else:
				bill.message = request.POST['message']
				bill.status = 'Rejected'
				bill.save()
				send_notification(request.session['email'], bill.creator_email, bid)
				return redirect(f'/customer/bill-details/{bid}/')
		return render(request, template_name, {'bill':bill,'error_message':'Wrong password'})
	context = {
		'bill':bill, 
		'email' :request.session['email'],
	}
	return render(request, template_name, context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def notifications(request):
	if 'email' not in request.session:
		return redirect('login')

	notifications = tuple(Notification.objects.filter(to_email=request.session['email']).order_by('-created_at'))
	if notifications:
		notifications = zip([i for i in range(1, len(notifications)+1)], notifications)
		return render(request, 'customer/notifications.html',{'notifications':notifications})
	return render(request, 'customer/notifications.html',{'status':'No Notifications Available'})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_bill(request, bid):
	if 'email' not in request.session:
		return redirect('login')
	try:
		template_name = 'customer/create_bill.html'
		bill = Bill.objects.get(pk=bid)

		if bill.receiver_email != request.session['email'] and bill.creator_email!=request.session['email']:
			return redirect('home')

		if request.method=='POST':
			status = save_bill(request, request.POST)
			if status == True:
				request.session['ustatus'] = 'Bill Created Successfully'
				return redirect(f'/customer/edit-bill/{request.POST["bid"]}/')
			context = {
				'bill': request.POST,
				'error_message':status if status else 'Enter valid date',
			}
			return render(request, template_name, context)
		elif 'ustatus' in request.session:
			status = request.session['ustatus']
			del request.session['ustatus']
			return render(request, template_name, {'status': status})
		return render(request, template_name, {'bill':bill})
	except Exception as e:
		return redirect('home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_bill(request, bid):
	if 'email' not in request.session:
		return redirect('login')
	try:
		bill = Bill.objects.get(pk=bid)

		if bill.creator_email!=request.session['email']:
			return redirect('home')
		bill.delete()
		return redirect('/customer/home/?s')
	except Exception as e:
		return redirect('home')


def send_notification(from_email, to_email, bid):
	Notification(
		from_email=from_email,
		to_email=to_email,
		bill_id=bid,
		created_at=timezone.now(),
	).save()
	

def save_bill(request, bill):
	try:

		month, day, year = [int(d) for d in bill['due_date'].split("/")]
		if date(year, month, day) < timezone.now().date():
			return "Due date should be greater than or equal to TODAY's date"
		bill_ = Bill()
		bill_.creator_email = request.session['email']
		bill_.creator_name = request.session['name']
		bill_.receiver_email = bill['receiver_email']
		bill_.receiver_name = bill['receiver_name']
		bill_.amount = bill['amount']
		bill_.product = bill['product']
		bill_.due_date = date(year, month, day)
		bill_.created_at = timezone.now()
		bill_.status = bill['status'] if 'status' in bill else 'Pending'

		if bill['bid']:
			bill_.id = int(bill['bid'])

		bill_.save()
	except Exception as e:
		return False
	return True












