from django.shortcuts import render

from reviews.forms import SearchForm
from reviews.models import Book
from reviews.utils import average_rating
from django.shortcuts import get_object_or_404


def book_list(request):
    form = SearchForm(request.GET)
    books = Book.objects.order_by('-publication_date')
    book_records = []

    if form.is_valid() and form.cleaned_data['search_in'] == 'title':
        books = books.filter(title__icontains=form.cleaned_data['search'])
    elif form.is_valid() and form.cleaned_data['search_in'] == 'contributor':
        books = books.filter(contributors__first_names__icontains=form.cleaned_data['search']) | \
            books.filter(contributors__last_names__icontains=form.cleaned_data['search'])

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

    return render(request, 'reviews/books_list.html', {
        'book_list': book_records,
        'form': form
    })


def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.review_set.order_by('-date_created')
    rating = average_rating([review.rating for review in reviews])

    return render(request, 'reviews/book_details.html', {'book': book, 'reviews': reviews, 'rating': rating})
