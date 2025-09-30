from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Category, Reservation
from datetime import date, timedelta

class ReservationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Fiction')
        self.book = Book.objects.create(
            title='Test Book',
            author='Author',
            category=self.category,
            isbn='1234567890123',
            total_copies=5,
            available_copies=5
        )
        self.reserve_url = reverse('reserve_book', args=[self.book.id])
        self.my_reservations_url = reverse('my_reservations')
        self.login_url = reverse('login')

    def test_reserve_book(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.reserve_url, {
            'contact_name': 'Test User',
            'contact_email': 'testuser@example.com'
        })
        self.assertRedirects(response, reverse('dashboard'))
        reservation = Reservation.objects.filter(user=self.user, book=self.book).first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.contact_name, 'Test User')
        self.assertEqual(reservation.contact_email, 'testuser@example.com')
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)

    def test_renew_reservation(self):
        self.client.login(username='testuser', password='testpass')
        reservation = Reservation.objects.create(
            user=self.user,
            book=self.book,
            contact_name='Test User',
            contact_email='testuser@example.com',
            due_date=date.today() + timedelta(days=7)
        )
        renew_url = reverse('renew_reservation', args=[reservation.id])
        response = self.client.get(renew_url)
        self.assertRedirects(response, self.my_reservations_url)
        reservation.refresh_from_db()
        self.assertEqual(reservation.due_date, date.today() + timedelta(days=14))
