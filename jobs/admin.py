from django.contrib import admin

from .models import Company, Job, Source, Search


admin.site.register(Company)
admin.site.register(Job)
admin.site.register(Source)
admin.site.register(Search)
