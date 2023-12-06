from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    SourceType,
    Example,
    FineTuningJob,
)  # Import your model here
from django.db.models import Q

from .finetune import *


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


class FineTuningJobAdmin(admin.ModelAdmin):
    list_display = ("openai_id", "created_at", "prior_model", "fine_tuned_model")
    list_filter = ("created_at", "prior_model")
    search_fields = ("openai_id", "prior_model", "fine_tuned_model")
    readonly_fields = ("created_at",)  # Make the 'created_at' field read-only


class ExampleAdmin(admin.ModelAdmin):
    list_display = (
        "created_by",
        "source_type",
        "prompt",
        "completion",
        "is_approved",
        # "was_processed",
        # "created_at",
        "updated_at",
        # "private_reference",
    )
    list_filter = ("is_approved", "created_by")
    search_fields = ("prompt_text", "completion_text", "private_note")

    def prompt(self, obj):
        return obj.prompt_text[:140] + "..." if obj.prompt_text else ""

    def completion(self, obj):
        return obj.completion_text[:140] + "..." if obj.completion_text else ""

    def save_model(self, request, obj, form, change):
        # Perform your custom action here
        # obj is the instance of MyModel being saved
        # You can access its attributes and modify them if needed
        # For example, you can perform additional processing or logging
        # Call the superclass's save_model method to save the object to the database
        # print("asdfasdfasdfasf")
        super().save_model(request, obj, form, change)
        # print("asdfasdfasdfasf")
        ready_for_fine_tuning = Example.objects.filter(
            Q(is_approved=True) & Q(fine_tuning_job__isnull=True)
        )
        jobs_still_running = FineTuningJob.objects.filter(fine_tuned_model__isnull=True)
        print(f"{ready_for_fine_tuning.count()} examples are ready for fine tuning")
        if ready_for_fine_tuning.count() >= 10 and jobs_still_running.count() == 0:
            print("fine tune")

        # else:
        #     print("don't fine tune")
        # print(f"{ready_for_fine_tuning.count()} examples are ready for fine tuning")
        # print(f"{ready_for_fine_tuning.count()} examples are ready for fine tuning")
        # print(f"{ready_for_fine_tuning.count()} examples are ready for fine tuning")
        # print("123412341234")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(FineTuningJob, FineTuningJobAdmin)
admin.site.register(Example, ExampleAdmin)
