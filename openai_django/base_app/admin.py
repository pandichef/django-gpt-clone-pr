from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    SourceType,
    Example,
    FineTuningJob,
)  # Import your model here
from django.db.models import Q
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.db.models import F, Case, When, Value, CharField, Q
from openai import OpenAI, BadRequestError

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
    list_display = (
        "openai_id",
        "created_at",
        "prior_model",
        "fine_tuned_model",
        "error_message",
        "job_status",
    )
    list_filter = (
        "created_at",
        "prior_model",
    )
    search_fields = ("openai_id", "prior_model", "fine_tuned_model")
    readonly_fields = (
        "created_at",
        "job_status",
    )  # Make the 'created_at' field read-only

    def job_status(self, obj):
        return obj.job_status

    # get_annotated_field.short_description = 'Annotated Field'

    # def custom_action(self, request, queryset):
    #     # Your custom logic here
    #     self.message_user(
    #         request, "Custom action was successfully performed on selected objects."
    #     )

    # actions = [custom_action]  # type: ignore

    change_list_template = "fine_tuning_job_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("process_approved_examples/", self.process_approved_examples),
            # path("mortal/", self.set_mortal),
        ]
        return my_urls + urls

    def process_approved_examples(self, request):
        qs = self.model.objects.all()
        qs_running = qs.filter(job_status="Running")
        examples_to_be_processed = Example.objects.all().filter(
            Q(is_approved=True) & Q(fine_tuning_job__isnull=True)
        )
        if qs_running.count() > 1:
            self.message_user(
                request,
                "Something went wrong.  Only one job can be running at the same time.",
            )
            return HttpResponseRedirect("../")
        elif qs_running.count() == 1:
            self.message_user(
                request,
                f"Job {qs_running.first().openai_id} still running. Try again later.",
            )
            return HttpResponseRedirect("../")
        elif (
            examples_to_be_processed.count()
            < settings.MINIMUM_NUMBER_OF_EXAMPLES_PER_OPENAI_JOB
        ):
            self.message_user(
                request,
                f"There are only {examples_to_be_processed.count()} examples to be process.  OpenAI requires at least 10 per job.",
            )
            return HttpResponseRedirect("../")
        else:  # default
            # successful_jobs = qs.filter(job_status="Success").order_by("created_at")
            # if successful_jobs.count() == 0:
            #     prior_model = settings.BASE_OPENAI_MODEL
            # else:
            #     last_successful_job = successful_jobs.last()
            #     prior_model = last_successful_job.fine_tuned_model
            prior_model = FineTuningJob.get_latest_openai_model()
            bytesio_object = write_records_to_bytesio(
                convert_to_openai_format(examples_to_be_processed)
            )

            client = OpenAI()
            openai_file_object = client.files.create(
                file=bytesio_object, purpose="fine-tune"
            )
            try:
                openai_ftjob_object = client.fine_tuning.jobs.create(
                    training_file=openai_file_object.id, model=prior_model,
                )
                new_fine_tuning_job = FineTuningJob.objects.create(
                    openai_id=openai_ftjob_object.id, prior_model=prior_model
                )
                new_fine_tuning_job.save()
                self.message_user(
                    # request, f"{openai_ftjob_object.status}",
                    request,
                    f"Successfully created OpenAI Fine-tuning Job.",
                )
                for example in examples_to_be_processed:
                    example.fine_tuning_job = new_fine_tuning_job
                    example.save()
                return HttpResponseRedirect("../")
            except BadRequestError as e:
                self.message_user(
                    request, f"{str(e)}",
                )
                return HttpResponseRedirect("../")

        # if self.model.objects.filter(job_status == "Running").count() > 0:
        #     self.message_user(request, "Job still running. Try again later")
        # self.model.objects.all().update(is_immortal=True)
        # return HttpResponseRedirect("../")

    # def set_mortal(self, request):
    #     self.model.objects.all().update(is_immortal=False)
    #     self.message_user(request, "All heroes are now mortal")
    #     return HttpResponseRedirect("../")


class ExampleAdmin(admin.ModelAdmin):
    readonly_fields = (
        "fine_tuning_job",
        "created_by",
    )
    list_display = (
        "is_approved",
        "fine_tuning_job",
        "created_by",
        "source_type",
        "prompt",
        "completion",
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
        obj.created_by = request.user
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
