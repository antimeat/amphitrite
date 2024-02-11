import smtplib
import email.message

def send_email(message, subject="Amphitrite hits the waves again! [SEC=UNOFFICIAL]", emoji="\U0001F3C4", sender="ImARobot@bom.gov.au", test_recipient="daz.vink@bom.gov.au", recipient="energy-resources-ops@bom.gov.au;leo.peach@bom.gov.au;daz.vink@bom.gov.au"):
    
    if emoji:
        subject = u"{} {}".format(emoji, subject)

    # msg = MIMEText(message)
    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.add_header('Content-Type','text/html')
    msg.set_payload(f"{message}")
    
    # Send the message via the server's configured MTA
    try:
        with smtplib.SMTP('localhost') as server:
            server.sendmail(sender, [recipient], msg.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")
