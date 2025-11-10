from django.contrib import admin

from classmatebot.subjects.models import Subject, Topic, Bite
# Register your models here.


class TopicInline(admin.StackedInline):
    model = Topic


class SubjectAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ('name', 'description', 'get_topics',)
    list_display_links = ('name',)
    search_fields = ('name',)
    inlines = [TopicInline] 
    

class BiteInline(admin.StackedInline):
    model = Bite    


class TopicAdmin(admin.ModelAdmin):
    fields = ['name', 'subject', 'description', 'content']
    list_display = ('name', 'subject', 'description')
    autocomplete_fields = ('subject',)
    inlines = [BiteInline]


class BiteAdmin(admin.ModelAdmin):
    fields = ['name', 'topic', 'bite']
    list_display = ('name', 'topic', 'bite')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Bite, BiteAdmin)    