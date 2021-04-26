import smtplib
from random import randint
from email.message import EmailMessage


def send_email(reciever_email, otp):
    msg = EmailMessage()
    msg.set_content(f"""
    Khata Record
    OTP: {otp}
    Don't Share with anyone
    We Don't call you and ask for OTP, Password and any other details
    """)

    msg['Subject'] = 'Khata Record OTP'
    msg['From'] = 'no.reply.message.otp@gmail.com'
    msg['To'] = reciever_email

    # Send the message via our own SMTP server.
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('no.reply.message.otp@gmail.com', "no.reply.otp")
        server.send_message(msg)
        server.quit()
    except:
        return False
    return True
