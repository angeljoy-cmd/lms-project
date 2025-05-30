from django.contrib import admin
from .models import Subject, Topic

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_name', 'teacher']
    filter_horizontal = ('students',)  # 👈 This allows assigning students in the admin

class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'subject', 'teacher']

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
