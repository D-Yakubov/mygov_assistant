from django.contrib import admin
from .models import GovService, ChatMessage

@admin.register(GovService)
class GovServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'keywords')
    search_fields = ('title', 'keywords')

admin.site.register(ChatMessage)