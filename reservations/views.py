from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Import models
from .models import Book, Reservation
from .forms import ReservationForm

@login_required
def dashboard(request):
    user_reservations = Reservation.objects.filter(user=request.user, returned=False)
    overdue_reservations = user_reservations.filter(due_date__lt=timezone.now().date())
    if overdue_reservations.exists():
        messages.warning(request, "You have overdue books! Please return or renew them.")
    total_books = Book.objects.count()
    return render(request, 'reservations/dashboard.html', {
        'total_books': total_books,
        'user_reservations_count': user_reservations.count(),
        'overdue_count': overdue_reservations.count(),
    })

@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
                Reservation.objects.create(
                    user=request.user,
                    book=book,
                    contact_name=form.cleaned_data['contact_name'],
                    contact_email=form.cleaned_data['contact_email']
                )
                messages.success(request, "Book reserved successfully!")
                return redirect('dashboard')
            else:
                messages.error(request, "No copies available.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()
    return render(request, 'reservations/reserve_book.html', {'book': book, 'form': form})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user, returned=False)
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})

@login_required
def renew_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.due_date += timedelta(days=7)
    reservation.save()
    messages.success(request, "Reservation renewed for 7 more days!")
    return redirect('my_reservations')

@login_required
def return_book(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if not reservation.returned:
        reservation.returned = True
        reservation.status = 'returned'
        reservation.save()
        reservation.book.available_copies += 1
        reservation.book.save()
        messages.success(request, f"Book '{reservation.book.title}' returned successfully!")
    else:
        messages.error(request, "Book already returned.")
    return redirect('my_reservations')
