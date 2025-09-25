from flask_mail import Mail, Message

mail = None  # we will initialize in app.py

def init_mail(app):
    """Initialize Flask-Mail with app config"""
    global mail
    mail = Mail(app)
    return mail

def send_booking_confirmation(recipient, guest_name, booking_id, hotel_name, checkin_date, checkout_date):
    """Send booking confirmation email with booking details"""
    try:
        msg = Message(
            subject=f"Booking Confirmation - {hotel_name} | PerfectStay",
            recipients=[recipient],
            body=f"""
Hello {guest_name},

Your booking has been successfully confirmed! 🎉  

📌 Booking Details:  
- Booking ID : {booking_id}  
- Hotel      : {hotel_name}  
- Check-in   : {checkin_date}  
- Check-out  : {checkout_date}  

We look forward to hosting you at {hotel_name}.  
Thank you for choosing PerfectStay!  

Warm Regards,  
PerfectStay Team
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False
