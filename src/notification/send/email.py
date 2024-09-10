import smtplib, os, json
from email.message import EmailMessage


def notification(message):

    try:
        message = json.loads(message)
        srt_fid = message["srt_fid"]
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_pass = os.environ.get("GMAIL_PASSWORD")
        receiver_address = message["username"]

        msg = EmailMessage()
        msg.set_content(f"Your SRT file is ready for download. \n\nSRT File ID: {srt_fid}")
        msg["Subject"] = "SRT File Ready"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.gmail.com")
        session.starttls()
        session.login(sender_address, sender_pass)

        session.send_message(msg, sender_address, receiver_address)
        session.quit()

        print(f"Email sent to {receiver_address}")
    except Exception as e:
        print(f"Error sending email: {e}")
        return e