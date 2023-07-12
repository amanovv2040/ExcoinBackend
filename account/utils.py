from django.core.mail import EmailMessage, EmailMultiAlternatives
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.content_subtype = 'html'
        EmailThread(email).start()
# class Util:
#     @staticmethod
#     def send_email(data):
#         subject = data['email_subject'],
#         body = data['email_body'],
#         to = data['to_email'],

#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=body,
#             to=to
#         )

#         email.attach_alternative(body, 'text/html')

#         EmailThread(email).start()
