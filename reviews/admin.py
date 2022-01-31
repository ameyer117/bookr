from django.contrib import admin

# Register your models here.
from reviews.models import Publisher, Contributor, Book, BookContributor, Review


class BookAdmin(admin.ModelAdmin):
    date_hierarchy = 'publication_date'
    search_fields = ('title', 'isbn')
    list_display = ('title', 'isbn')
    list_filter = ('publisher', 'publication_date')


class ReviewAdmin(admin.ModelAdmin):
    exclude = ('date_edited',)


admin.site.register(Publisher)
admin.site.register(Contributor)
admin.site.register(Book, BookAdmin)
admin.site.register(BookContributor)
admin.site.register(Review, ReviewAdmin)

