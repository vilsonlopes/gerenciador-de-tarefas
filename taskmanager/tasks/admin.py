from django.contrib import admin
from .models import Task


# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'status', 'owner', 'created_at', 'updated_at')
    list_filter = ('status',)
    actions = ['mark_archived']

    def mark_archived(self, request, queryset):
        queryset.update(status='ARCHIVED')

    mark_archived.short_description = 'Mark selected tasks as archived'

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('tasks.change_task'):
            return True
        return False

    def has_add_permission(self, request):
        if request.user.has_perm('tasks.add_task'):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('tasks.delete_task'):
            return True
        return False


admin.site.register(Task, TaskAdmin)
