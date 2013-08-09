from django.contrib import admin
from clubreview.models import *

class ClubURIEditAdmin(admin.ModelAdmin):
  def approve(modeladmin, request, queryset):
    for edit in queryset.all():
        edit.handle_attribute_save(ClubURIEdit.APPROVED_STATE)
  def deny(modeladmin, request, queryset):
      for edit in queryset.all():
        edit.handle_attribute_save(ClubURIEdit.DENIED_STATE)
  deny.short_description = "Mark URL as invalid"
  approve.short_description = "Set club url to be this value"
  list_display = ['club', 'value', 'display_attribute_type', 'attribute_type', 'display_state', 'state']
  list_editable = ['value']
  ordering = ( 'club', 'value')
  actions = [approve, deny]
class ClubAdmin(admin.ModelAdmin):
  list_display = ['name', 'facebook_url', 'website', 'SGID']
  list_editable = ['facebook_url', 'website', 'SGID']
  ordering = ( 'name', )

admin.site.register(Event)
admin.site.register(School)
admin.site.register(Review)
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubURIEdit, ClubURIEditAdmin)


