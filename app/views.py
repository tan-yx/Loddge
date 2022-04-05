from django.shortcuts import render, redirect
from django.db import connection

from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

def register(request):
    context = {}
    status = ''
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        context['form'] = form
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            group = Group.objects.get(name='user')
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + email)
            print('Register User:', request.POST)
            # POST request: create in user_base table
            if request.POST['action'] == 'register':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM user_base WHERE email = %s", [request.POST['email']])
                    user = cursor.fetchone()
                ## No user with same id
                if user == None:
                    ##TODO: date validation
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO user_base VALUES (%s, %s, %s, %s)", 
                                        [request.POST['email'], 
                                        request.POST['first_name'],
                                        request.POST['last_name'] , 
                                        request.POST['phone_number']])
        
                else: 
                    status = 'User with email %s already exists' % (request.POST['email'])
            return redirect("/login")
        else:
            print('Invalid Form')
            messages.error(request, 'Form is Invalid. Try again with valid details.')
    else:
        context['status'] = status
        context['form'] = CreateUserForm()
    return render(request, 'registration/register.html', context)


# Create your views here.
def index(request):
    """Shows the main page"""
    return render(request,'app/index.html')

# Create your views here.
def view(request, id):
    """Shows view page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM listings WHERE listing_id = %s", [id])
        listing = cursor.fetchone()
    result_dict = {'list': listing}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    """Shows add page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM listings WHERE listing_id = %s", [request.POST['listing_id']])
            customer = cursor.fetchone()
            ## No listing with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO listings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['listing_id'], request.POST['listing_name'], request.POST['neighbourhood'],
                           request.POST['neighbourhood_group'] , request.POST['address'],
                           request.POST['room_type'] , request.POST['price'], request.POST['owner_id'], request.POST['total_occupancy'],
                           request.POST['total_bedrooms'] , request.POST['has_internet'], request.POST['has_aircon'], request.POST['has_kitchen'],
                           request.POST['has_heater'] ])
                return redirect('index')    
            else:
                status = 'Listing with ID %s already exists' % (request.POST['listing_id'])
                
    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    """Shows edit page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM listings WHERE listing_id = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute(
               """
               UPDATE listings SET listing_id = %s, 
                   listing_name = %s, neighbourhood = %s, 
                   neighbourhood_group = %s, address = %s, 
                   room_type = %s,price = %s,owner_id = %s,
                   total_occupancy = %s,total_bedrooms = %s,
                   has_internet = %s,has_aircon = %s,
                   has_kitchen = %s,has_heater = %s 
               WHERE listing_id = %s
               """
            , [request.POST['listing_id'], request.POST['listing_name'], request.POST['neighbourhood'],
                   request.POST['neighbourhood_group'] , request.POST['address'],
                   request.POST['room_type'] , request.POST['price'], request.POST['owner_id'], request.POST['total_occupancy'],
                   request.POST['total_bedrooms'] , request.POST['has_internet'], request.POST['has_aircon'], request.POST['has_kitchen'],
                   request.POST['has_heater'], id ])
            status = 'Listing edited successfully!'
            cursor.execute("SELECT * FROM listings WHERE listing_id = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)

def reservations(request):
    """Shows the reservations table"""
    context = {}
    status = ''
    
    ## Delete listing
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", [request.POST['idR']])
    
    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * 
                FROM  reservations r
                WHERE reservation_id = %s 
                ORDER BY r.reservation_id
                """,
                [
                    request.POST['reservation_id']
                ])                
                listings = cursor.fetchall()

            result_dictR = {'recordsR': reservations}

            return render(request,'app/reservations.html', result_dictR)
    else:
        context['status'] = status
        ## Use sample query to get listings

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * 
                FROM reservations r
                ORDER BY r.reservation_id
                """
                ),
            reservations = cursor.fetchall()

        result_dictR = {'recordsR': reservations}

        return render(request,'app/reservations.html', result_dictR)

    
    

def marketplace(request):
    """Shows the listings table"""
    context = {}
    status = ''
    
    ## Delete listing
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM listings WHERE listing_id = %s", [request.POST['id']])
    
    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * 
                FROM  listings l
                WHERE neighbourhood_group = %s 
                AND total_occupancy = %s 
                ORDER BY l.listing_id
                """,
                [
                    request.POST['neighbourhood_group'],
                    request.POST['total_occupancy']
                ])                
                listings = cursor.fetchall()

            result_dict = {'records': listings}

            return render(request,'app/marketplace.html', result_dict)
    else:
        context['status'] = status
        ## Use sample query to get listings

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * 
                FROM listings l
                ORDER BY l.listing_id
                """
                ),
            listings = cursor.fetchall()

        result_dict = {'records': listings}

        return render(request,'app/marketplace.html', result_dict)
