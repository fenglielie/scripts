#!/usr/bin/env python3

import argparse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser
from datetime import datetime

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
    except Exception as e:
        print(f"Error: Failed to read file '{file_path}'. Error: {e}")
    return None

def prepare_email_body(body_start, file_paths):
    max_files = 3
    max_content_length = 4000  # Maximum length to truncate content

    body_parts = []

    # Add body start if provided
    if body_start:
        body_parts.append(body_start)

    error_messages = []

    for file_path in file_paths[:max_files]:
        content = read_file_content(file_path)
        if content is not None:  # Check if the file was read successfully
            if content:  # Check if the content is not empty
                # Add file name and boundaries at the beginning and end of each file content
                body_parts.append(f"\n\n----- File '{file_path}' Start -----\n")
                # Truncate content if too long
                if len(content) > max_content_length:
                    content = content[:max_content_length//2] + "\n...\n" + content[-(max_content_length//2):]
                body_parts.append(content)
                body_parts.append(f"\n----- File '{file_path}' End -----\n\n")
            else:
                # Content is an empty string
                body_parts.append(f"\n\n----- File '{file_path}' Start -----\n")
                body_parts.append("This file is empty.\n")
                body_parts.append(f"----- File '{file_path}' End -----\n\n")
        else:
            error_messages.append(f"Failed to read file '{file_path}'")


    # Add error messages to the body
    if error_messages:
        body_parts.append("\n\n----- Error Log -----\n")
        body_parts.append("\n".join(error_messages))

    return "\n".join(body_parts)

def send_email(subject, body, sender, receiver, host, port, username, password):
    # Create email message
    message = MIMEText(body, "plain", "utf-8")
    message["From"] = sender
    message["To"] = receiver

    # Add timestamp to the email subject
    subject_with_timestamp = f"{subject} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
    message["Subject"] = Header(subject_with_timestamp, "utf-8")

    # Send email
    try:
        smtpObj = smtplib.SMTP_SSL(host, port)
        smtpObj.login(username, password)
        smtpObj.sendmail(sender, receiver, message.as_string())
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email. Error: {e}")
    finally:
        smtpObj.quit() if 'smtpObj' in locals() else None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Send Email')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body_start', help='Initial string of email body')
    parser.add_argument('-f', '--files', nargs='+', help='Up to 3 text file paths as email body')
    parser.add_argument('-c', '--config', default='config.ini', help='Configuration file path, default is config.ini')
    args = parser.parse_args()

    # Create configparser object
    config = configparser.ConfigParser()

    # Read configuration file
    config.read(args.config)

    # Get email configuration
    mail_user = config.get('email', 'username')
    mail_pass = config.get('email', 'password')
    sender = config.get('email', 'sender')
    receiver = config.get('email', 'receiver')
    host = config.get('email', 'host')
    port = config.getint('email', 'port')

    # Prepare email body
    if args.files:
        body = prepare_email_body(args.body_start, args.files)
    elif args.body_start:
        body = args.body_start
    else:
        body = "Nothing but ..."

    # Send email
    send_email(args.subject, body, sender, receiver, host, port, mail_user, mail_pass)

if __name__ == "__main__":
    main()

'''
[email]
username = xxxxxxxxxxxxxxxx@163.com
password = xxxxxxxxxxxxxxxx
sender = xxxxxxxxxxxxxxxx@163.com
receiver = xxxxxxxxxxxxxxxx@qq.com
host = smtp.163.com
port = 465
'''
