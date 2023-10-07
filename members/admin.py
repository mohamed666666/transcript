from django.contrib import admin
from .models import Member

class MemberAdmin(admin.ModelAdmin):
      list_display = ("first_name", "last_name", "date_of_birth", 'email')
  
admin.site.register(Member, MemberAdmin)