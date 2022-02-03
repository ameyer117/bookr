from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from reviews.forms import SearchForm, PublisherForm, ReviewForm
from reviews.models import Book, Publisher, Review
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


def book_reviews_list(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    reviews = book.review_set.order_by('-date_created')
    return render(request, 'reviews/book_reviews_list.html', {'book': book, 'reviews': reviews})


def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None

    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher:
                messages.info(request, f"Publisher {updated_publisher} was updated.")
            else:
                messages.success(request, f"Publisher {updated_publisher} was created.")
            return redirect("publisher_edit", updated_publisher.pk)
        else:
            return render(request, "reviews/instance-form.html", {'method': request.method, 'form': form})
    else:
        form = PublisherForm(instance=publisher)
        return render(request, "reviews/instance-form.html", {'method': request.method, 'form': form})


def review_edit(request, book_pk, review_pk=None):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_pk)
        if review_pk:
            review = get_object_or_404(Review, pk=review_pk)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                saved_review = form.save(commit=False)
                saved_review.book = book
                saved_review.date_edited = timezone.now()
                saved_review.save()
                messages.success(request, "Updated review successfully")
                return redirect('review_edit', book_pk, saved_review.pk)
            else:
                return render(request, "reviews/instance-form.html", {'method': request.method, 'form': form})
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                saved_review = form.save(commit=False)
                saved_review.book = book
                saved_review.date_edited = timezone.now()
                saved_review.save()
                messages.success(request, "Created review successfully")
                return redirect("book_reviews_list", book_pk)
            else:
                return render(request, "reviews/instance-form.html", {'method': request.method, 'form': form})
    else:
        if review_pk:
            instance = get_object_or_404(Review, pk=review_pk)
            form = ReviewForm(instance=instance)
        else:
            form = ReviewForm()
        return render(request, "reviews/instance-form.html", {'method': request.method, 'form': form})
