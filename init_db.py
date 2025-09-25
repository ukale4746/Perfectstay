import sqlite3

conn = sqlite3.connect("hotels.db")
c = conn.cursor()

# -------------------
# Create users table
# -------------------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    phone TEXT,
    password TEXT
)
""")

# -------------------
# Create hotels table
# -------------------
c.execute("""
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    price INTEGER NOT NULL,
    rating REAL,
    image_url TEXT,
    description TEXT
)
""")

# -------------------
# Create amenities table
# -------------------
c.execute("""
CREATE TABLE IF NOT EXISTS amenities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER,
    amenity TEXT,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
)
""")

# -------------------
# Create bookings table with payment status
# -------------------
c.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER,
    guest_name TEXT,
    checkin_date TEXT,
    checkout_date TEXT,
    guests INTEGER,
    total_price REAL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
)
""")

# -------------------
# Insert sample hotels if table is empty
# -------------------
c.execute("SELECT COUNT(*) FROM hotels")
if c.fetchone()[0] == 0:
    hotels_data = [
        ("Sea View Resort", "Goa", 2999, 4.7, "https://imgs.search.brave.com/inT4ZWAzCrKLw1DWaxXgeeXQqPElI4tCTcE7aNoAnok/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9hdy1k/LnRyaXBjZG4uY29t/L2ltYWdlcy8yMjBh/MWIwMDAwMDFhemJ2/OUVBM0RfV181MDBf/NDAwX1I1LndlYnA_/ZGVmYXVsdD0x", "Sea View Resort offers comfortable rooms with modern amenities, perfect for a beach vacation."),
        ("Grand Palace", "Jaipur", 3999, 4.8, "https://imgs.search.brave.com/F7zJjSkgeY_wT94_fzkDF8t8lAMDV6bWvkGHBAagsuA/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly90aHJp/bGxpbmd0cmF2ZWwu/aW4vd3AtY29udGVu/dC91cGxvYWRzLzIw/MjMvMTAvQ2hhbmRy/YS1tYWhhbC1jaXR5/LXBhbGFjZS1qYWlw/dXIuanBn", "Grand Palace offers luxurious stays with royal architecture and top-class services."),
        ("City Lights Inn", "Mumbai", 2499, 4.5, "https://imgs.search.brave.com/gvGT07Kj7Qq8tXipKhlzLxVzFA7YiIBi2KsVCzecQzM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZi5i/c3RhdGljLmNvbS94/ZGF0YS9pbWFnZXMv/aG90ZWwvMjcweDIw/MC80NzQzMjk0Mzku/anBnP2s9ZmM5MTNk/NWYxMjZjMjNmMTIz/ZmE2Njg3ZjM0OGE5/MGZmZDRiNWE4OTli/NjkxYjg4ZjljMzY5/OTdjNDMyZjE2MyZv/PQ", "City Lights Inn is located in the heart of Mumbai and offers modern rooms with city views.")
    ]
    c.executemany("INSERT INTO hotels (name, location, price, rating, image_url, description) VALUES (?, ?, ?, ?, ?, ?)", hotels_data)

# -------------------
# Insert sample amenities if table is empty
# -------------------
c.execute("SELECT COUNT(*) FROM amenities")
if c.fetchone()[0] == 0:
    amenities_data = [
        (1, "Free WiFi"), (1, "Swimming Pool"), (1, "Breakfast Included"), (1, "Sea View"), (1, "Parking"),
        (2, "Free WiFi"), (2, "Spa"), (2, "Breakfast Included"), (2, "Gym"), (2, "Parking"),
        (3, "Free WiFi"), (3, "Air Conditioning"), (3, "Breakfast Included"), (3, "Parking"), (3, "Gym")
    ]
    c.executemany("INSERT INTO amenities (hotel_id, amenity) VALUES (?, ?)", amenities_data)

# -------------------
# Optional: Insert sample bookings
# -------------------
c.execute("SELECT COUNT(*) FROM bookings")
if c.fetchone()[0] == 0:
    bookings_data = [
        (1, "Alice", "2025-09-20", "2025-09-22", 2, 2999*2, "Paid"),
        (2, "Bob", "2025-09-25", "2025-09-28", 3, 3999*3, "Pending"),
    ]
    c.executemany("INSERT INTO bookings (hotel_id, guest_name, checkin_date, checkout_date, guests, total_price, status) VALUES (?, ?, ?, ?, ?, ?, ?)", bookings_data)

conn.commit()
conn.close()
print("Database initialized and ready with payment status and user support!")
