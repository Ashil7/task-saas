from django.contrib import admin
from .models import User, Organization, Membership, Projects, Task

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register([Projects])
admin.site.register(Task)



