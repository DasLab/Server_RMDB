from repository.models import *
from django.contrib import admin

class ConstructInLine(admin.StackedInline):
    model = ConstructSection
    extra = 0

class EntryAnnotationInLine(admin.TabularInline):
    model = EntryAnnotation
    extra = 1

class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryAnnotationInLine, ConstructInLine]
    list_display = ('id', 'rmdb_id', 'version', 'short_description', 'revision_status')

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('pubmed_id', 'title', 'authors')

class OrganismAdmin(admin.ModelAdmin):
    list_display = ('taxonomy_id', 'name')

class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('date', 'title')

admin.site.register(RMDBEntry, EntryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Organism, OrganismAdmin)

