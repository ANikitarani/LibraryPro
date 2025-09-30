from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, OuterRef, Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

# Import models
from .models import Book, Category, Reservation   # ✅ add Reservation here
from .forms import ReservationForm

@login_required
def dashboard(request):
    user_reservations = Reservation.objects.filter(user=request.user, returned=False)
    overdue_reservations = user_reservations.filter(due_date__lt=timezone.now().date())
    if overdue_reservations.exists():
        messages.warning(request, "You have overdue books! Please return or renew them.")
    return render(request, 'books/dashboard.html', {
        'user_reservations_count': user_reservations.count(),
        'overdue_count': overdue_reservations.count(),
    })

@login_required
def catalog(request):
    query = request.GET.get('q')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(category__name__icontains=query)
        )
    return render(request, 'books/catalog.html', {'books': books})
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
                return redirect('catalog')
            else:
                messages.error(request, "No copies available.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()
    return render(request, 'books/reserve_book.html', {'book': book, 'form': form})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user, returned=False)
    return render(request, 'books/my_reservations.html', {'reservations': reservations})

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
@login_required
def send_overdue_alerts(request):
    overdue = Reservation.objects.filter(due_date__lt=timezone.now().date(), returned=False, notified=False)
    for r in overdue:
        r.status = 'overdue'
        r.notified = True
        r.save()
        send_mail(
            'LibraryPro - Overdue Book Alert',
            f'Hello {r.contact_name}, your book "{r.book.title}" is overdue!',
            'librarypro@example.com',
            [r.contact_email],
        )
    messages.info(request, "Overdue alerts sent!")
    return redirect('catalog')
@login_required
def analytics(request):
    total_books = Book.objects.count()
    total_reservations = Reservation.objects.count()
    active_reservations = Reservation.objects.filter(returned=False).count()
    overdue_reservations = Reservation.objects.filter(due_date__lt=timezone.now().date(), returned=False).count()
    popular_books = Book.objects.annotate(reservation_count=Count('reservation')).order_by('-reservation_count')[:5]
    return render(request, 'books/analytical.html', {
        'total_books': total_books,
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
        'overdue_reservations': overdue_reservations,
        'popular_books': popular_books,
    })
