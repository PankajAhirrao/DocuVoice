from django.contrib import admin

# Register your models here.
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'uploaded_at')  # Columns displayed in admin
    search_fields = ('file_name', 'user__username')  # Enable search functionality
    list_filter = ('uploaded_at',)  # Add a filter sidebar
    ordering = ('-uploaded_at',)  # Order by newest uploaded first
