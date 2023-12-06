from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SourceType, Example  # Import your model here


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    # list_display = [
    #     "email",
    #     "username",
    # ]


class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ExampleAdmin(admin.ModelAdmin):
    list_display = (
        "prompt_text",
        "completion_text",
        "is_approved",
        "created_by",
        "created_at",
        "updated_at",
        "reference",
        "source_type",
    )
    list_filter = ("is_approved", "created_by")
    search_fields = ("prompt_text", "completion_text")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Example, ExampleAdmin)
