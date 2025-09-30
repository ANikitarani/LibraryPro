from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from books.models import Reservation

class Command(BaseCommand):
    help = 'Send email notifications for overdue reservations'

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_reservations = Reservation.objects.filter(
            due_date__lt=today,
            returned=False,
            notified=False
        )

        for reservation in overdue_reservations:
            # Update status to overdue
            reservation.status = 'overdue'
            reservation.notified = True
            reservation.save()

            # Send email
            subject = 'LibraryPro - Overdue Book Alert'
            message = f'Hello {reservation.contact_name},\n\nYour reserved book "{reservation.book.title}" is overdue. Please return it as soon as possible to avoid fines.\n\nDue Date: {reservation.due_date}\n\nThank you,\nLibraryPro Team'
            from_email = 'librarypro@example.com'
            recipient_list = [reservation.contact_email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                self.stdout.write(
                    self.style.SUCCESS(f'Sent overdue notification to {reservation.contact_email} for book "{reservation.book.title}"')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send email to {reservation.contact_email}: {e}')
                )

        if not overdue_reservations:
            self.stdout.write('No overdue reservations to notify.')
