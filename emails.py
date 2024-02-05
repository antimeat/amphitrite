import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_email(message, subject="Amphitrite hits the waves again! [SEC=UNOFFICIAL]", emoji="\U0001F3C4", sender="daz.vink@bom.gov.au", test_recipient="daz.vink@bom.gov.au", recipient="energy-resources-ops@bom.gov.au"):
    
    if emoji:
        subject = u"{} {}".format(emoji, subject)

    msg = MIMEText(message)
    msg['Subject'] = Header(subject, 'utf-8')  # Ensure proper encoding with Unicode
    msg['From'] = sender
    msg['To'] = test_recipient

    # Send the message via the server's configured MTA
    try:
        with smtplib.SMTP('localhost') as server:
            server.sendmail(sender, [test_recipient], msg.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")
