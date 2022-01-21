from django.shortcuts import render

from reviews.models import Book
from reviews.utils import average_rating
from django.shortcuts import get_object_or_404


def book_list(request):
    books = Book.objects.order_by('-publication_date')
    book_records = []

    for book in books:
        reviews = book.review_set.all()
        if reviews:
            book_rating = average_rating([review.rating for review in reviews])
            number_of_reviews = len(reviews)
        else:
            book_rating = None
            number_of_reviews = 0
        book_records.append({
            'book': book,
            'book_rating': book_rating,
            'number_of_reviews': number_of_reviews
        })

        context = {
            'book_list': book_records
        }

    return render(request, 'reviews/books_list.html', context)


def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.review_set.order_by('-date_created')
    rating = average_rating([review.rating for review in reviews])

    return render(request, 'reviews/book_details.html', {'book': book, 'reviews': reviews, 'rating': rating})
