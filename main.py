# Import Flask
from flask import Flask, request, render_template, redirect, session
import random
from datetime import timedelta
from flask_mysqldb import MySQL

app = Flask(__name__)

# Secret key for the application to avoid attacks
app.config['SECRET_KEY'] = 'af9f4f6f73b4189cb815d04b90b5fc1d035f386c5b474fbc65d2f1'
app.permanent_session_lifetime = timedelta(minutes=30)

# Setting up database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'airline_project'

mysql = MySQL(app)

# Default Route
@app.route("/", methods=["POST", "GET"])
def home():
    # Generating a seven-digit random number
    random_number = random.randint(1000000,9999999)
    
    if request.method == "GET":
        if "p_name" in session:
            return redirect("/passenger-home-page")

    if request.method == "POST":

        # Capturing User Input
        p_id = request.form["pid"]
        p_id = int(p_id)
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        address = request.form["address"]
        age = request.form["age"]
        age = int(age)
        contact = request.form["contact"]
        contact = int(contact)

        # Storing User Input in a dictionary
        passenger_details = {
            "Passenger_id":p_id,
            "Name":name,
            "Email":email,
            "Password":password,
            "Address":address,
            "Age":age,
            "Contact":contact
        }

        # Creating a connection cursor
        cursor = mysql.connection.cursor()

        # Inserting passenger details into DB
        cursor.execute("INSERT INTO passenger_registration(p_id, p_name, p_email, p_password, p_address, p_age, p_contact) VALUES(%s,%s,%s,%s,%s,%s,%s)", (p_id, name, email, password, address, age, contact))

        # Saving the Actions performed on the DB
        mysql.connection.commit()

        # Closing the cursor
        cursor.close()

        print("Registration Successful")
        return render_template("PassengerRegistration/successfulRegistration.html", p_id = p_id, name = name, email = email, title="Account Created")

    else:
        return render_template("PassengerRegistration/passengerRegistration.html", random_number=random_number, title="Register")

# Login Route
@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":

        # Making session permanent
        session.permanent = True

        # Storing input data into variables
        p_name = request.form["name"]
        p_password = request.form["password"]

        # Creating a connection cursor
        cursor = mysql.connection.cursor()

        # SELECT query to check if the passenger name exists in DB
        cursor.execute("SELECT p_name FROM passenger_registration WHERE p_name=%(p_name)s",{'p_name':p_name})

        # Fetching one value from database and storing it in the variable
        select_name = cursor.fetchone()

        # IF block will get executed if name is not found in database
        if not select_name:
            print("No account found!")
            return redirect("/login")

        # ELSE block will get executed if name exists in DB
        else:

            # SELECT query to check if password matches with the name
            cursor.execute("SELECT p_password FROM passenger_registration WHERE p_password=%(p_password)s", {'p_password':p_password})

            # Fetching one value from database and storing it in the variable
            select_password = cursor.fetchone()

            # IF block will get executed if password does not match
            if not select_password:
                print("No account found!")
                return redirect("/login")

            # ELSE block will get executed if password matches
            else:

                # return render_template("TicketBooking/passengerHome.html", p_name = p_name)

                # Storing passenger name in the session
                session["p_name"] = p_name
                return redirect("/passenger-home-page")
    else:

        # IF block gets executed if passenger name is in session
        if "p_name" in session:
            return redirect("/passenger-home-page")

        # ELSE block gets executed if passenger name is not in session
        else:
            return render_template("Login/login.html", title="Login")

# Passenger Home Page Route
@app.route("/passenger-home-page", methods=["POST", "GET"])
def passengerHome():

    # IF block gets executed if passenger name is in session
    if "p_name" in session:
        p_name = session["p_name"]
        return render_template("TicketBooking/passengerHome.html", p_name=p_name, title="Home")

    # ELSE block gets executed if passenger name is not in session and is redirect to login    
    else:
        return redirect("/login")

@app.route("/logout")
def logout():

    # IF block gets executed if method is GET
    if request.method == "GET":

        # Deleting passenger name from session
        session.pop("p_name", None)
        return redirect("/login")

# Ticket Booking Route
@app.route("/book-ticket", methods=["POST", "GET"])
def bookTicket():

    # IF block gets executed if method is GET
    if request.method == "GET":

        # IF block gets executed if passenger name is in session
        if "p_name" in session:
            pnr = random.randint(1000000,9999999)
            p_name = session["p_name"]
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT p_id FROM passenger_registration WHERE p_name=%(p_name)s", {"p_name":p_name})
            select_id = cursor.fetchone()
            if select_id:
                p_id = select_id[0]
            return render_template("TicketBooking/bookTicket.html", title="Book Ticket", pnr=pnr, p_id=p_id)
        
        # ELSE redirect to the login page
        else:
            return redirect("/login")

    # IF the form is submitted
    if request.method == "POST":

        # Capturing the data into variables
        passenger_id = request.form["p_id"]
        pnr = request.form["pnr"]
        date = request.form["date"]
        source_airport = request.form["source"]
        destination_airport = request.form["destination"]
        ticket_status = request.form["status"]
        seat_preference = request.form["seat"]
        meal_preference = request.form["meal"]

        # Storing the variables into a dictionary
        booking_details = {
            "Passenger ID":passenger_id,
            "PNR Number":pnr,
            "Date":date,
            "Source Airport":source_airport,
            "Destination Airport":destination_airport,
            "Ticket Status":ticket_status,
            "Seat Preference":seat_preference,
            "Meal Preference":meal_preference
        }

        # Creating a cursor
        cursor = mysql.connection.cursor()

        # Inserting booking details using INSERT query
        cursor.execute('''
            INSERT INTO ticket_booking(
                pnr,
                ticket_date,
                source_airport,
                destination_airport,
                ticket_status,
                seat_preference,
                meal_preference,
                passenger_id
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (
            pnr,
            date,
            source_airport,
            destination_airport,
            ticket_status,
            seat_preference,
            meal_preference,
            passenger_id
        ))

        # Commiting all the actions
        mysql.connection.commit()

        # Closing the cursor
        cursor.close()

        return render_template(
            "TicketBooking/successfulBooking.html",
            title="Ticket Booked",
            pnr=pnr,
            ticket_date=date,
            source_airport=source_airport,
            destination_airport=destination_airport
        )

# View Tickets Route
@app.route("/view-tickets", defaults={"table":1})
@app.route("/view-tickets/table/<int:table>")
def view_tickets(table):
    if request.method == "GET":

        # Only 5 records per table
        limit = 5
        offset = table * limit - limit

        # If user is logged in, then IF block gets executed
        if "p_name" in session:
            p_name = session["p_name"]

            # Creating a cursor
            cursor = mysql.connection.cursor()

            # SELECT query for getting the passenger id of the logged in user
            cursor.execute("SELECT p_id FROM passenger_registration WHERE p_name=%(p_name)s", {"p_name":p_name})

            # Fetching the passenger id
            select_id = cursor.fetchone()

            # IF block gets executed if passenger id is fetched
            if select_id:

                # Storing passenger id in the variable
                passenger_id = select_id[0]
                passenger_id = str(passenger_id)

            # Variable for next and previous table(pagination)
            next = table + 1
            prev = table - 1

            # SELECT query for getting the booking history of passenger
            cursor.execute("SELECT * FROM ticket_booking WHERE passenger_id=%s LIMIT %s OFFSET %s", (passenger_id, limit, offset))

            # Fetching booking history
            select_all = list(cursor.fetchall())

            return render_template("TicketBooking/bookingHistory.html", title="View History", booking_history=select_all, next=next, prev=prev)
        
        # Redirect to login if not in session
        else:
            return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)