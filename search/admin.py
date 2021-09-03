from django.contrib import admin
from search.models import SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'datetime', 'result', 'user']
