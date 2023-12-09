from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from django.db.models import F, Case, When, Value, CharField, Q


base_openai_model = "gpt-3.5-turbo-1106"
# base_openai_model = "gpt-4" # on waitlist


class CustomUser(AbstractUser):
    pass


class SourceType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class FineTuningJobManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        qs = qs.annotate(
            job_status=Case(
                When(
                    Q(error_message__isnull=True) & Q(fine_tuned_model__isnull=True),
                    then=Value("Running"),
                ),
                When(
                    Q(error_message__isnull=True) & Q(fine_tuned_model__isnull=False),
                    then=Value("Success"),
                ),
                When(
                    Q(error_message__isnull=False) & Q(fine_tuned_model__isnull=True),
                    then=Value("Failed"),
                ),
                default=Value(
                    "Something went wrong. Error message should be null or Fine-funed should be null"
                ),
                output_field=CharField(),
            )
        )
        return qs


class FineTuningJob(models.Model):
    openai_id = models.CharField(max_length=256, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prior_model = models.CharField(max_length=256, null=False, blank=False)
    # post-completion
    # status = models.CharField(max_length=256, null=True, blank=True)
    error_message = models.CharField(max_length=256, null=True, blank=True)
    fine_tuned_model = models.CharField(max_length=256, null=True, blank=True)

    objects = FineTuningJobManager()

    @classmethod
    def get_latest_openai_model(cls):
        successful_jobs = cls.objects.filter(job_status="Success").order_by(
            "created_at"
        )
        if successful_jobs.count() == 0:
            prior_model = base_openai_model  # settings.BASE_OPENAI_MODEL
            # prior_model = "gpt-4-0613"  # settings.BASE_OPENAI_MODEL
        else:
            last_successful_job = successful_jobs.last()
            prior_model = last_successful_job.fine_tuned_model
        return prior_model

    @classmethod
    def get_lastest_update_date(cls):
        openai_model_name = cls.get_latest_openai_model()
        if openai_model_name == base_openai_model:
            return f"Never updated.  Using {base_openai_model}."
        else:
            last_job = cls.objects.get(fine_tuned_model=openai_model_name)
            return f"Last updated {last_job.updated_at.date()} using base model {base_openai_model}."

    def __str__(self):
        return f"{str(self.openai_id)}"


class Example(models.Model):
    prompt_text = models.TextField()
    completion_text = models.TextField()
    is_approved = models.BooleanField(
        default=False, help_text="Approved for fine-tuning"
    )
    # was_processed = models.BooleanField(
    #     default=False, help_text="Processed in a prior fine-tuning run"
    # )
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_type = models.ForeignKey(
        SourceType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The source of the record",
    )
    private_reference = models.URLField(
        null=True, blank=True, help_text="Not used in fine-tuning"
    )
    # reference = models.URLField(max_length=200, blank=True)
    private_note = models.TextField(
        null=True, blank=True, help_text="Not used in fine-tuning"
    )
    fine_tuning_job = models.ForeignKey(
        FineTuningJob, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return (
            f"Example created by {self.created_by.username} on {self.created_at.date()}"
        )
