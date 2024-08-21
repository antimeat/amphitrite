#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import argparse
import smtplib
import email.message

def send_email(message, subject="Poseidon & Amphitrite in development! [SEC=UNOFFICIAL]", emoji="\U0001F3C4", sender="robot", recipient="energy-resources-ops;davink@wa-vw-er.bom.gov.au"):
    if emoji:
        subject = f"{emoji} {subject}"

    recipients = recipient.split(';')  # Handles multiple recipients separated by ';'

    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(f"{message}")
    
    try:
        with smtplib.SMTP('localhost') as server:
            server.sendmail(sender, recipients, msg.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Error: {e}")

def success(message):
    send_email(message, subject="Success: Amphitrite [SEC=UNOFFICIAL]", emoji="\U0001F389")  # Success emoji

def fail(message):
    send_email(message, subject="Failure: Amphitrite [SEC=UNOFFICIAL]", emoji="\U0001F4A5")  # Explosion emoji

def main():
    parser = argparse.ArgumentParser(description="Send notification emails based on success or failure of processes.")
    parser.add_argument('--success', action='store_true', help='Flag this email as a success notification.')
    parser.add_argument('--fail', action='store_true', help='Flag this email as a failure notification.')
    parser.add_argument('--message', type=str, required=True, help='Message to be included in the email.')
    
    args = parser.parse_args()

    if args.success:
        success(args.message)
    elif args.fail:
        fail(args.message)
    else:
        print("No action specified. Use --success or --fail to specify the email type.")

if __name__ == "__main__":
    main()
