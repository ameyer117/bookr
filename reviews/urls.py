from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>', views.book_details, name="book_details"),
    path('publishers/<int:pk>/', views.publisher_edit, name='publisher_edit'),
    path('publishers/new/', views.publisher_edit, name='publisher_create'),
    path('reviews/<int:book_pk>/', views.book_reviews_list, name='book_reviews_list'),
    path('reviews/<int:book_pk>/<int:review_pk>', views.review_edit, name='review_edit'),
    path('reviews/<int:book_pk>/new/', views.review_edit, name='review_create'),
]
