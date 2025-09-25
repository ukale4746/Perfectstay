from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import sqlite3
from datetime import datetime
import razorpay

# import mail utility functions
from email_utils import init_mail, send_booking_confirmation

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "hotels.db"

# Mail Config(mail sttings for gmail)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USERNAME"] = "hotelsofheaven@gmail.com"      
app.config["MAIL_PASSWORD"] = "tqoa iysj bcvx dxrb"           
app.config["MAIL_DEFAULT_SENDER"] = "hotelsofheaven@gmail.com"

mail = init_mail(app)  # initialize mail


# Razorpay Config
# Razorpay Settings
RAZORPAY_KEY_ID = "rzp_test_RIFEpoG2Eb6nVn"
RAZORPAY_KEY_SECRET = "2S7JmrvE1xDu2aKaZCDlwl2E"
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# Database Helper(conection)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db:
        db.close()


# Home Page(opens home page of the website)


@app.route("/")
def home():
    db = get_db()
    featured_hotels = db.execute("SELECT * FROM hotels LIMIT 6").fetchall()

    # Predefined popular cities (or fetch distinct from DB)
    popular_cities = [
        {"name": "Mumbai", "image_url": "https://imgs.search.brave.com/u4r6R23iz704b34jtpdXVY52CvPinKsHwFDUx3t8aEY/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly90My5m/dGNkbi5uZXQvanBn/LzA4LzQ3LzIyLzk2/LzM2MF9GXzg0NzIy/OTYzMF94WlJDaXZJ/b3FXc01sYzNCa0Q3/RFo4YVBKUmdET1c5/cy5qcGc"},
        {"name": "Delhi", "image_url": "https://imgs.search.brave.com/d1vGW95za_LilxhM8tOdeYinZEhU3RzJZkcrSI75hww/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9oYmxp/bWcubW10Y2RuLmNv/bS9jb250ZW50L2h1/YmJsZS9pbWcvZGVs/aGkvbW10L2FjdGl2/aXRpZXMvbV9hY3Rp/dml0aWVzX2RlbGhp/X2luZGlhX2dhdGVf/NV9sXzUwNV83NTgu/anBn"},
        {"name": "Goa", "image_url": "https://imgs.search.brave.com/62GuhRdigCloKsBhmkGmoJKVvy6xDoNGbeMHIrOI3R4/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMjIw/NTgzODk2OC9waG90/by9pbmRpYS1nb2Et/c3RhdGUtbmVydWwt/cmVpcy1tYWdvcy1m/b3J0LmpwZz9zPTYx/Mng2MTImdz0wJms9/MjAmYz1yLUNveldE/djYtMWtLd1pXU1VV/amFjMjYxWU9hYTZs/dHo5WGpOQXowTndR/PQ"},
        {"name": "Pune", "image_url": "https://imgs.search.brave.com/QdYVvwJ_T_iqESj6c3Tap7tOJEOYwNICQoEyjA33GNk/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly93YW5k/ZXJvbi1pbWFnZXMu/Z3VtbGV0LmlvL2Js/b2dzL25ldy8yMDI0/LzA3L3NoYW5pd2Fy/LXdhZGEtYW4tb3Zl/cnZpZXcuanBn"},
    ]

    return render_template("home.html", 
                           featured_hotels=featured_hotels, 
                           popular_cities=popular_cities)


# Listings Page route

@app.route("/listings", methods=["GET"])
def listing():
    db = get_db()
    
    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    location = request.args.get("location")
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    max_price = request.args.get("max_price")
    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    min_rating = request.args.get("min_rating")
    if min_rating:
        query += " AND rating >= ?"
        params.append(min_rating)

    hotels = db.execute(query, params).fetchall()
    return render_template("listing.html", hotels=hotels)


# Registration page route{setting up user registration}

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)",
                (username, email, phone, password)
            )
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# Login (user authentication)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        if not username:
            flash("Username is required", "danger")
            return redirect(url_for("login"))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            flash("User not found. Please register first.", "danger")
            return redirect(url_for("register"))

        session["user"] = username
        flash(f"Welcome, {username}!", "success")
        return redirect(url_for("home"))

    return render_template("login.html")

# Logout (end user session)


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out", "info")
    return redirect(url_for("home"))


# Profile
#fetches user data from db and displays it along with their bookings

@app.route("/profile")
def profile():
    if "user" not in session:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

    username = session["user"]
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

    bookings = db.execute("""
        SELECT b.id, h.name, h.location, b.checkin_date, b.checkout_date, b.guests, b.total_price, COALESCE(b.status,'Pending')
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.guest_name=?
        ORDER BY b.checkin_date DESC
    """, (username,)).fetchall()

    return render_template("profile.html", user=user, bookings=bookings)


# Hotel Detail

@app.route("/hotel/<int:hotel_id>")
def hotel_detail(hotel_id):
    db = get_db()
    hotel = db.execute("SELECT * FROM hotels WHERE id=?", (hotel_id,)).fetchone()
    if not hotel:
        return "Hotel not found", 404

    amenities = db.execute("SELECT amenity FROM amenities WHERE hotel_id=?", (hotel_id,)).fetchall()
    amenities = [a["amenity"] for a in amenities]

    hotel = dict(hotel)
    hotel["latitude"] = 18.5204
    hotel["longitude"] = 73.8567

    return render_template("hotel_detail.html", hotel=hotel, amenities=amenities)

# Add Hotel
# enables admin to add new hotels to the database

@app.route("/admin/add_hotel", methods=["GET", "POST"])
def admin_add_hotel():
    # Ensure only admin can access
    if "admin" not in session:
        flash("Please log in as admin", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form["name"].strip()
        location = request.form["location"].strip()
        price = request.form["price"].strip()
        rating = request.form["rating"].strip()
        image_url = request.form["image_url"].strip()
        description = request.form["description"].strip()
        amenities = request.form.get("amenities", "").split(",")

        db = get_db()
        cursor = db.execute(
            "INSERT INTO hotels (name, location, price, rating, image_url, description) VALUES (?, ?, ?, ?, ?, ?)",
            (name, location, price, rating, image_url, description)
        )
        hotel_id = cursor.lastrowid

        # Add amenities
        for amenity in amenities:
            amenity = amenity.strip()
            if amenity:
                db.execute("INSERT INTO amenities (hotel_id, amenity) VALUES (?, ?)", (hotel_id, amenity))

        db.commit()
        flash(f"Hotel '{name}' added successfully!", "success")
        return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard after adding

    # GET request: show admin add hotel form
    return render_template("add_hotel.html")



# Remove Hotel
@app.route("/admin/remove_hotel", methods=["GET", "POST"])
def admin_remove_hotel():
    # Ensure only admin can access
    if "admin" not in session:
        flash("Please log in as admin", "danger")
        return redirect(url_for("admin_login"))

    db = get_db()

    if request.method == "POST":
        hotel_id = request.form["hotel_id"]
        db.execute("DELETE FROM amenities WHERE hotel_id=?", (hotel_id,))
        db.execute("DELETE FROM hotels WHERE id=?", (hotel_id,))
        db.commit()
        flash("Hotel removed successfully!", "success")
        return redirect(url_for("admin_dashboard"))  # Redirect to admin dashboard

    # GET request: show list of hotels to remove
    hotels = db.execute("SELECT * FROM hotels").fetchall()
    return render_template("remove_hotel.html", hotels=hotels)


# Book Hotel with Razorpay
# integrates Razorpay payment gateway for booking payments

@app.route("/hotel/<int:hotel_id>/book", methods=["GET", "POST"])
def book_hotel(hotel_id):
    db = get_db()
    hotel = db.execute("SELECT * FROM hotels WHERE id=?", (hotel_id,)).fetchone()
    if not hotel:
        return "Hotel not found", 404

    if request.method == "POST":
        guest_name = request.form["guest_name"]
        checkin = request.form["checkin"]
        checkout = request.form["checkout"]
        guests = request.form["guests"]

        checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
        checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
        nights = max((checkout_date - checkin_date).days, 1)
        total_price = hotel["price"] * nights

        # Create Razorpay order
        payment = client.order.create({
            "amount": total_price * 100,  # in paise(1 INR = 100 paise)
            "currency": "INR",
            "payment_capture": "1"
        })

        # Save booking as Pending
        cursor = db.execute(
            "INSERT INTO bookings (hotel_id, guest_name, checkin_date, checkout_date, guests, total_price, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (hotel_id, guest_name, checkin, checkout, guests, total_price, "Pending")
        )
        booking_id = cursor.lastrowid
        db.commit()

        session["booking_id"] = booking_id
        session["guest_name"] = guest_name

        return render_template(
            "payment.html",
            hotel=hotel,
            payment=payment,
            guest_name=guest_name,
            total_price=total_price,
            key_id=RAZORPAY_KEY_ID
        )

    return render_template("booking_form.html", hotel=hotel)

# Payment Success
#send success email after payment
@app.route("/payment_success", methods=["POST"])
def payment_success():
    booking_id = session.get("booking_id")
    guest_name = session.get("guest_name")

    if not booking_id or not guest_name:
        flash("Payment session expired", "danger")
        return redirect(url_for("home"))

    db = get_db()
    db.execute("UPDATE bookings SET status=? WHERE id=?", ("Paid", booking_id))
    db.commit()

    # Fetch booking details (hotel + dates)
    booking = db.execute("""
        SELECT b.id, b.checkin_date, b.checkout_date, h.name AS hotel_name
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.id=?
    """, (booking_id,)).fetchone()

    # Fetch user email
    user = db.execute("SELECT email FROM users WHERE username=?", (guest_name,)).fetchone()
    recipient_email = user["email"] if user else app.config["MAIL_USERNAME"]

    # Send confirmation email
    success = send_booking_confirmation(
        recipient=recipient_email,
        guest_name=guest_name,
        booking_id=booking_id,
        hotel_name=booking["hotel_name"],
        checkin_date=booking["checkin_date"],
        checkout_date=booking["checkout_date"]
    )

    if success:
        flash("Payment successful! Confirmation email sent.", "success")
    else:
        flash("Payment successful, but email failed to send.", "warning")

    return redirect(url_for("my_bookings"))


# My Bookings
# displays user's bookings

@app.route("/my_bookings")
def my_bookings():
    if "user" not in session:
        flash("Please log in to view your bookings", "danger")
        return redirect(url_for("login"))

    guest_name = session["user"]
    db = get_db()
    bookings = db.execute("""
        SELECT b.id, h.name, h.location, b.checkin_date, b.checkout_date, b.guests, b.total_price, COALESCE(b.status,'Pending')
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.guest_name=?
        ORDER BY b.checkin_date DESC
    """, (guest_name,)).fetchall()
    return render_template("my_bookings.html", bookings=bookings, guest_name=guest_name)

#Enables users to cancel their bookings
# Cancel Booking

@app.route("/cancel_booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user" not in session:
        flash("Please log in to cancel bookings", "danger")
        return redirect(url_for("login"))

    db = get_db()
    db.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    db.commit()
    flash("Your booking has been cancelled successfully!", "success")
    return redirect(url_for("my_bookings"))

# Search Hotels

@app.route("/search", methods=["GET"])
def search():
    db = get_db()
    
    location = request.args.get("location")
    checkin = request.args.get("checkin")
    checkout = request.args.get("checkout")

    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    hotels = db.execute(query, params).fetchall()

    if not hotels:
        flash("No hotels found for your search!", "info")

    return render_template("listing.html", hotels=hotels)

# About Page route
@app.route("/about")
def about():
    return render_template("about.html")

# Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Simple hardcoded credentials (change as needed)
        if username == "admin" and password == "admin123":
            session["admin"] = True
            flash("Welcome Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


# Admin Dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        flash("Please log in as admin", "danger")
        return redirect(url_for("admin_login"))

    db = get_db()
    hotels = db.execute("SELECT * FROM hotels").fetchall()
    bookings = db.execute("""
        SELECT b.id, h.name AS hotel_name, b.guest_name, b.checkin_date, b.checkout_date, b.guests, b.total_price, COALESCE(b.status,'Pending')
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        ORDER BY b.checkin_date DESC
    """).fetchall()
    users = db.execute("SELECT * FROM users").fetchall()

    return render_template("admin_dashboard.html", hotels=hotels, bookings=bookings, users=users)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out", "info")
    return redirect(url_for("admin_login"))


# Run App
#start the Flask application

if __name__ == "__main__":
    app.run(debug=True)
