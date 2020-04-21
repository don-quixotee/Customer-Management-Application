from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate , login , logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required




from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter


# Create your views here.

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account successfully created for ' +user )
                return redirect('login')


        context = {'form':form}
        return render(request, 'account/register.html', context)

    
        
    # form = CreateUserForm()

    # if request.method == 'POST':
    #     form = CreateUserForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         user = form.cleaned_data.get('username')
    #         messages.success(request, 'Account successfully created for ' +user )
    #         return redirect('login')


    # context = {'form':form}
    # return render(request, 'account/register.html', context)


def loginPage(request):


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is Invalid')

    context = {}
    return render(request, 'account/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')



@login_required(login_url = 'login')
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status = 'Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders, 'customers':customers, 'total_orders':total_orders, 
    'total_customers': total_customers, 'pending':pending , 'delivered':delivered }
    return render(request, 'account/dashboard.html', context)

@login_required(login_url = 'login')
def products(request):
    products = Product.objects.all()
    return render(request, 'account/products.html',{'products':products})


@login_required(login_url = 'login')
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()
    order_count= orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {'customer':customer, 'orders':orders, 'order_count':order_count, 'myFilter':myFilter}
    return render(request, 'account/customer.html',context )

@login_required(login_url = 'login')
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer,Order,fields=('product','status'), extra=6)
    customer = Customer.objects.get(id=pk)

    # form = OrderForm(initial={'customer':customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)


    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST,instance=customer)

        if formset.is_valid():
            formset.save()
            return redirect('/')

    context= {'formset': formset}
    return render(request, 'account/order_form.html', context)


@login_required(login_url = 'login')
def updateOrder(request, pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    


    context = {'form': form}
    return render(request, 'account/order_form.html', context)


@login_required(login_url = 'login')
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
     
    if request.method == "POST":
        order.delete()
        return redirect('/')

    context = {'item':order}

    return render(request, 'account/delete.html', context)
