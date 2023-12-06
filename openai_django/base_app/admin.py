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
        "created_by",
        "source_type",
        "prompt",
        "completion",
        "is_approved",
        # "created_at",
        "updated_at",
        # "private_reference",
    )
    list_filter = ("is_approved", "created_by")
    search_fields = ("prompt_text", "completion_text")

    def prompt(self, obj):
        return obj.prompt_text[:140] + "..." if obj.prompt_text else ""

    def completion(self, obj):
        return obj.completion_text[:140] + "..." if obj.completion_text else ""


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Example, ExampleAdmin)
