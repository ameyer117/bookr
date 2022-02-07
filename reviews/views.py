import os
from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.images import ImageFile
from django.shortcuts import render, redirect
from django.utils import timezone

from reviews.forms import SearchForm, PublisherForm, ReviewForm, BookMediaForm
from reviews.models import Book, Publisher, Review
from reviews.utils import average_rating, build_search_history
from django.shortcuts import get_object_or_404


def is_staff_user(user):
    return user.is_staff


def book_list(request):
    form = SearchForm(request.GET)
    books = Book.objects.order_by('-publication_date')
    book_records = []

    if form.is_valid() and form.cleaned_data['search']:
        search_history = request.session.get('search_history', [])
        new_search = [form.cleaned_data['search'], form.cleaned_data['search_in']]
        request.session['search_history'] = build_search_history(search_history, new_search)
        if form.cleaned_data['search_in'] == 'title':
            books = books.filter(title__icontains=form.cleaned_data['search'])
        elif form.cleaned_data['search_in'] == 'contributor':
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


def book_details(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    reviews = book.review_set.order_by('-date_created')
    rating = average_rating([review.rating for review in reviews])

    if request.user.is_authenticated:
        max_viewed_books_length = 10
        viewed_books = request.session.get('viewed_books', [])
        viewed_book = [book.id, book.title]
        if viewed_book in viewed_books:
            viewed_book.pop(viewed_books.index(viewed_book))
        viewed_books.insert(0, viewed_book)
        viewed_books = viewed_books[:max_viewed_books_length]
        request.session['viewed_books'] = viewed_books

    return render(request, 'reviews/book_details.html', {'book': book, 'reviews': reviews, 'rating': rating})


def book_reviews_list(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    reviews = book.review_set.order_by('-date_created')
    return render(request, 'reviews/book_reviews_list.html', {'book': book, 'reviews': reviews})


@user_passes_test(is_staff_user)
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
            return render(request, "reviews/instance-form.html",
                          {'method': request.method, 'form': form, 'model': 'Publisher'})
    else:
        form = PublisherForm(instance=publisher)
        return render(request, "reviews/instance-form.html",
                      {'method': request.method, 'form': form, 'model': 'Publisher'})


@login_required
def review_edit(request, book_pk, review_pk=None):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_pk)
        if review_pk:
            review = get_object_or_404(Review, pk=review_pk)
            if not request.user.is_staff and review.creator.id != request.user.id:
                raise PermissionDenied()

            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                saved_review = form.save(commit=False)
                saved_review.book = book
                saved_review.date_edited = timezone.now()
                saved_review.save()
                messages.success(request, "Updated review successfully")
                return redirect('review_edit', book_pk, saved_review.pk)
            else:
                return render(request, "reviews/instance-form.html",
                              {'method': request.method, 'form': form, 'model': 'Review'})
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
                return render(request, "reviews/instance-form.html",
                              {'method': request.method, 'form': form, 'model': 'Review'})
    else:
        if review_pk:
            instance = get_object_or_404(Review, pk=review_pk)
            if not request.user.is_staff and instance.creator.id != request.user.id:
                raise PermissionDenied()

            form = ReviewForm(instance=instance)
        else:
            form = ReviewForm()
        return render(request, "reviews/instance-form.html",
                      {'method': request.method, 'form': form, 'model': 'Review'})


@login_required
def book_media(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)

    if request.method == 'POST':
        form = BookMediaForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(False)
            cover = form.cleaned_data['cover']

            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 500))
                image_data = BytesIO()
                image.save(fp=image_data, format=image.format)
                image_file = ImageFile(image_data)
                book.cover.save(cover.name, image_file)

            book.save()
            return redirect("book_details", book_pk)

    form = BookMediaForm(instance=book)
    return render(request, "reviews/instance-form.html",
                  {'method': request.method, 'form': form, 'is_file_form': True, 'model': 'Media'})
