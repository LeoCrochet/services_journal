from django.contrib import admin

from .models import Branch, UserProfile


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "prefix", "signer_name", "signer_position")
    fields = ("name", "code", "prefix", "signer_name", "signer_position")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch")
    list_filter = ("role", "branch")