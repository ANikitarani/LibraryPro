from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('renew/<int:reservation_id>/', views.renew_reservation, name='renew_reservation'),
    path('return/<int:reservation_id>/', views.return_book, name='return_book'),
    path('overdue-alerts/', views.send_overdue_alerts, name='overdue_alerts'),
    path('analytics/', views.analytics, name='analytics'),
]
