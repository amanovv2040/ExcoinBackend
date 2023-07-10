from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_created')
    list_display_links = list_display
    search_fields = ('name', 'email', 'date_created', 'text')