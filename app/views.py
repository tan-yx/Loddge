from django.shortcuts import render, redirect
from django.db import connection

def login(request):
    context = {}
    status = ""
    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_password FROM user_base WHERE user_id = %s", 
                           [request.POST["user_id"]])
            customers = cursor.fetchone()
        if customers == None:
            status = "Login failed, no such user. Please create an account."
        elif customers[0] == "admin@admin.com":
            if customers[1] == request.POST["user_password"]:
                status = "Login successful."
                return redirect('admin_page')
            else:
                status = "Login failed, wrong password."
        else:
            if customers[1] == request.POST["user_password"]:
                status = "Login successful."
                return redirect('home_user', id = request.POST["user_id"])
            else:
                status = "Login failed, wrong password."
    context["status"] = status
    return render(request,'app/login.html', context)

def register(request):
    """Shows the main page"""
    context = {}
    status = ''
    if request.POST:
        ## Check if userid is already in the table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_base WHERE user_id = %s", [request.POST['user_id']])
            user = cursor.fetchone()
            ## No user with same id
            if user == None:
                cursor.execute("INSERT INTO user_base VALUES (%s, %s, %s, %s, %s)", 
                               [request.POST['user_id'],
                                request.POST['user_password'], 
                                request.POST['first_name'],
                                request.POST['last_name'] , 
                                request.POST['phone_number']])
                return redirect('login')    
            else:
                status = 'User with ID %s already exists' % (request.POST['user_id'])
    context['status'] = status
    return render(request, "app/register.html", context)

def dashboard(request):
    """Shows the admin dashboard"""
    context = {}
    status = ''

    context['status'] = status
    ## Use sample query to get listings
    """Top 10 Revenue-Generating Listings"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.listing_name,
            SUM((upper(r.date_range) - lower(r.date_range)) * l.price) AS total_revenue
            FROM reservations r, listings l
            WHERE r.listing_id = l.listing_id
            GROUP BY l.listing_name
            ORDER BY total_revenue DESC
            LIMIT 10
            """
            ),
        totalrev = cursor.fetchall()
        result_dictRev = {'recordsRev': totalrev}
        
    """Top 10 Revenue-Generating Neighbourhoods and their Number of Listings"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.neighbourhood,
                SUM((upper(r.date_range) - lower(r.date_range)) * l.price) AS total_revenue,
            COUNT(*) as number_of_listings
            FROM reservations r, listings l
            WHERE r.listing_id = l.listing_id
            GROUP BY l.neighbourhood
            ORDER BY total_revenue DESC
            LIMIT 10
            """
            ),
        totalrevL = cursor.fetchall()
        result_dictRevL = {'recordsRevL': totalrevL}
        
    """Top 20% of Owners with the Greatest Revenues"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.owner_id, u.first_name, u.last_name,
                SUM((upper(r.date_range) - lower(r.date_range)) * l.price) AS total_revenue
            FROM reservations r, listings l, user_base u
            WHERE r.listing_id = l.listing_id
                AND l.owner_id = u.user_id
            GROUP BY l.owner_id, u.first_name, u.last_name
            ORDER BY total_revenue DESC
            LIMIT (SELECT COUNT(DISTINCT owner_id)*0.2 FROM listings)
            """
            ),
        totalO = cursor.fetchall()
        result_dictO = {'recordsO': totalO}
        
    """Top 20% of Listings by Average Review"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.listing_id, l.listing_name,
            AVG(rev.review)::NUMERIC(3,2) AS average_review
            FROM reviews rev, reservations res, listings l
            WHERE rev.reservation_id = res.reservation_id
            AND res.listing_id = l.listing_id
            GROUP BY l.listing_id, l.listing_name
            ORDER BY average_review DESC
            LIMIT (SELECT COUNT(DISTINCT listing_name)*0.2 FROM listings)
            """
            ),
        totalA = cursor.fetchall()
        result_dictA = {'recordsA': totalA}
        
    """Top 20% of Users with the Highest Number of Reservations"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.user_id, u.first_name, u.last_name, COUNT(*) AS total_reservations
            FROM reservations r, user_base u
            WHERE r.user_id = u.user_id
            GROUP BY r.user_id, u.first_name, u.last_name
            ORDER BY total_reservations DESC
            LIMIT(SELECT COUNT(DISTINCT user_id)*0.2 FROM reservations)
            """
            ),
        totalB = cursor.fetchall()
        result_dictB = {'recordsB': totalB}
        
    """Top 20% of Listing Owners with the Highest Number of Reservations under their Listings"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.owner_id, u.first_name, u.last_name, COUNT(*) AS total_listings
            FROM listings l, user_base u
            WHERE l.owner_id = u.user_id
            GROUP BY l.owner_id, u.first_name, u.last_name
            ORDER BY total_listings DESC
            LIMIT (SELECT COUNT(DISTINCT owner_id)*0.2 FROM listings)
            """
            ),
        totalC = cursor.fetchall()
        result_dictC = {'recordsC': totalC}

    return render(request,'app/dashboard.html', {'recordsRev': totalrev, 'recordsRevL': totalrevL, 'recordsO': totalO, 'recordsA': totalA, 'recordsB': totalB, 'recordsC': totalC})

def admin_page(request):
    """Shows the admin page"""
    return render(request,'app/admin_page.html')

def landing(request):
    """Shows the landing page"""
    return render(request,'app/landing.html')

# Create your views here.
def home(request):
    """Shows the home page after login"""
    return render(request,'app/home.html')

# Create your views here.
def view(request, id):
    """Shows view page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM listings WHERE listing_id = %s", [id])
        listing = cursor.fetchone()
    result_dict = {'list': listing}

    return render(request,'app/view.html',result_dict)

def view_reservations(request, id):
    """Shows reservations for specified listing"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM reservations WHERE listing_id = %s", [id])
        listing = cursor.fetchall()
    result_dict = {'records': listing}

    return render(request,'app/view_reservations.html',result_dict)

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
                return redirect('marketplace')    
            else:
                status = 'Listing with ID %s already exists' % (request.POST['listing_id'])
                
    context['status'] = status
 
    return render(request, "app/add.html", context)

def add_user(request):
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
                return redirect('marketplace_user')    
            else:
                status = 'Listing with ID %s already exists' % (request.POST['listing_id'])
                
    context['status'] = status
 
    return render(request, "app/add.html", context)

def addreservation(request):
    context = {}
    status = ''

    if request.POST:
        ## Check if already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", [request.POST['reservation_id']])
            customer = cursor.fetchone()
            ## No listing with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO reservations VALUES (%s, %s, %s, %s)"
                        , [request.POST['reservation_id'], request.POST['user_id'], request.POST['listing_id'],
                           request.POST['date_range'] ])
                return redirect('addreservation')    
            else:
                status = 'Reservation with ID %s already exists' % (request.POST['reservation_id'])
                
    context['status'] = status
 
    return render(request, "app/addreservation.html", context)

def addreservation_user (request):
    context = {}
    status = ''

    if request.POST:
        ## Check if already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", [request.POST['reservation_id']])
            customer = cursor.fetchone()
            ## No listing with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO reservations VALUES (%s, %s, %s, %s)"
                        , [request.POST['reservation_id'], request.POST['user_id'], request.POST['listing_id'],
                           request.POST['date_range'] ])
                return redirect('addreservation_user')    
            else:
                status = 'Reservation with ID %s already exists' % (request.POST['reservation_id'])
                
    context['status'] = status
 
    return render(request, "app/addreservation_user.html", context)

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

def editR(request, id):
    """Shows edit page for reservations"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute(
               """
               UPDATE reservations SET 
                   reservation_id = %s,
                   user_id = %s,
                   listing_id = %s,
                   date_range = %s
               WHERE reservation_id = %s
               """
            , [request.POST['reservation_id'], 
               request.POST['user_id'], 
               request.POST['listing_id'],
               request.POST['date_range'],
               id ])
            status = 'Reservation edited successfully!'
            cursor.execute("SELECT * FROM reservations WHERE reservation_id = %s", [id])
            obj = cursor.fetchone()
            
    context["obj"] = obj
    context["status"] = status
    
    return render(request, "app/editR.html", context)

def reservations(request):
    """Shows the reservations table"""
    context = {}
    status = ''
    
    ## Delete listing
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", [request.POST['idR']])
         
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
                reservations = cursor.fetchall()

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

def home_user(request, id):
    """Shows the home page for each user"""
    context = {}
    status = ''
    
    ## Delete reservation
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", [request.POST['idR']])
    else:
        context['status'] = status
        ## Use sample query to get listings

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * 
                FROM reservations r
                WHERE user_id = %s
                ORDER BY r.reservation_id
                """
                , [id]),
            reservations = cursor.fetchall()

        result_dictR = {'recordsR': reservations}

        return render(request,'app/home_user.html', result_dictR)
    

def marketplace(request):
    """Shows the listings table"""
    context = {}
    status = ''
    
    ## Delete listing
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM listings WHERE listing_id = %s", [request.POST['id']])
            
            context['status'] = status
            ## Use sample query to get listings
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT l.listing_id,
                        l.listing_name,
                        l.neighbourhood, l.neighbourhood_group, l.address, l.room_type,
                        l.price, CASE WHEN a.average_review is NULL THEN 0 ELSE a.average_review END,
                        l.owner_id, l.total_occupancy, l.total_bedrooms
                    FROM
                        listings l
                    LEFT JOIN
                    (SELECT res.listing_id,
                    AVG(rev.review)::NUMERIC(3,2) AS average_review
                    FROM reviews rev, reservations res
                    WHERE rev.reservation_id = res.reservation_id
                    GROUP BY res.listing_id) AS a
                    ON l.listing_id = a.listing_id
                    ORDER BY l.listing_id
                    """
                    ),
                listings = cursor.fetchall()

            result_dict = {'records': listings}

            return render(request,'app/marketplace.html', result_dict)
    
    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM
                (SELECT l.listing_id,
                    l.listing_name,
                    l.neighbourhood, l.neighbourhood_group, l.address, l.room_type,
                    l.price, CASE WHEN a.average_review is NULL THEN 0 ELSE a.average_review END,
                    l.owner_id, l.total_occupancy, l.total_bedrooms
                FROM
                    listings l
                LEFT JOIN
                (SELECT res.listing_id,
                AVG(rev.review)::NUMERIC(3,2) AS average_review
                FROM reviews rev, reservations res
                WHERE rev.reservation_id = res.reservation_id
                GROUP BY res.listing_id) AS a
                ON l.listing_id = a.listing_id
                ORDER BY l.listing_id) AS b
                WHERE neighbourhood_group = %s
                    AND total_occupancy >= %s
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
                SELECT l.listing_id,
                    l.listing_name,
                    l.neighbourhood, l.neighbourhood_group, l.address, l.room_type,
                    l.price, CASE WHEN a.average_review is NULL THEN 0 ELSE a.average_review END,
                    l.owner_id, l.total_occupancy, l.total_bedrooms
                FROM
                    listings l
                LEFT JOIN
                (SELECT res.listing_id,
                AVG(rev.review)::NUMERIC(3,2) AS average_review
                FROM reviews rev, reservations res
                WHERE rev.reservation_id = res.reservation_id
                GROUP BY res.listing_id) AS a
                ON l.listing_id = a.listing_id
                ORDER BY l.listing_id
                """
                ),
            listings = cursor.fetchall()

        result_dict = {'records': listings}

        return render(request,'app/marketplace.html', result_dict)
    
def marketplace_user(request):
    """Shows the listings table"""
    context = {}
    status = ''

    if request.POST:
        if request.POST['action'] == 'search':
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM
                (SELECT l.listing_id,
                    l.listing_name,
                    l.neighbourhood, l.neighbourhood_group, l.address, l.room_type,
                    l.price, CASE WHEN a.average_review is NULL THEN 0 ELSE a.average_review END,
                    l.owner_id, l.total_occupancy, l.total_bedrooms
                FROM
                    listings l
                LEFT JOIN
                (SELECT res.listing_id,
                AVG(rev.review)::NUMERIC(3,2) AS average_review
                FROM reviews rev, reservations res
                WHERE rev.reservation_id = res.reservation_id
                GROUP BY res.listing_id) AS a
                ON l.listing_id = a.listing_id
                ORDER BY l.listing_id) AS b
                WHERE neighbourhood_group = %s
                    AND total_occupancy >= %s
                """,
                [
                    request.POST['neighbourhood_group'],
                    request.POST['total_occupancy']
                ])                
                listings = cursor.fetchall()

            result_dict = {'records': listings}

            return render(request,'app/marketplace_user.html', result_dict)
    else:
        context['status'] = status
        ## Use sample query to get listings

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT l.listing_id,
                    l.listing_name,
                    l.neighbourhood, l.neighbourhood_group, l.address, l.room_type,
                    l.price, CASE WHEN a.average_review is NULL THEN 0 ELSE a.average_review END,
                    l.owner_id, l.total_occupancy, l.total_bedrooms
                FROM
                    listings l
                LEFT JOIN
                (SELECT res.listing_id,
                AVG(rev.review)::NUMERIC(3,2) AS average_review
                FROM reviews rev, reservations res
                WHERE rev.reservation_id = res.reservation_id
                GROUP BY res.listing_id) AS a
                ON l.listing_id = a.listing_id
                ORDER BY l.listing_id
                """
                ),
            listings = cursor.fetchall()

        result_dict = {'records': listings}

        return render(request,'app/marketplace_user.html', result_dict)
