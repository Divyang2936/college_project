from django.contrib import admin
from .models import Course, CustomUser, Role

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display=['name','created_at','updated_at']


admin.site.register(CustomUser)
admin.site.register(Role)
# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
    # list_display = ['role']