from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.UserProfile)
admin.site.register(models.UserProjects)
admin.site.register(models.UserAssets)
admin.site.register(models.UserPks)
admin.site.register(models.OtherAPIAdmin)
