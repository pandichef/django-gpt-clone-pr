from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from django.db.models import F, Case, When, Value, CharField, Q
from django.conf import settings

# base_openai_model = "gpt-3.5-turbo-1106"
# base_openai_model = "gpt-4" # on waitlist
base_openai_model = settings.BASE_OPENAI_MODEL


# class Search(models.Lookup):
#     lookkup_name = "search"


# def as_mysql(self, compiler, connection):
#     lhs, lhs_params = self.process_lhs(compiler, connection)
#     rhs, rhs_params = self.process_rhs(compiler, connection)
#     params = lhs_params + rhs_params
#     return "MATCH (%s) AGAINST (%s IN BOOLEAN MODE)" % (lhs, rhs), params


# models.CharField.register_lookup(Search)
# models.TextField.register_lookup(Search)


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

    @classmethod
    def get_search_results(cls, search_text):
        """
        The following must be run first
        ALTER TABLE base_app_example ADD FULLTEXT INDEX (prompt_text, completion_text);
        See https://database.guide/how-the-match-function-works-in-mysql/
        https://www.promptingguide.ai/techniques/rag

        migrations.RunSQL(
            sql="ALTER TABLE base_app_example ADD FULLTEXT INDEX (prompt_text, completion_text);"
        ), # added to initial migration
        """
        # qs = cls.objects.all()
        # select * from base_app_example where match(prompt_text, completion_text) against('{search_text}')
        search_text = search_text.replace("'", "''")
        minimum_relevance_score = 0
        return Example.objects.raw(
            f"""
SELECT 
  id, MATCH(prompt_text, completion_text) AGAINST('{search_text}') AS relevance
FROM base_app_example
WHERE MATCH(prompt_text, completion_text) AGAINST('{search_text}') > {minimum_relevance_score}
ORDER BY relevance DESC;
"""
        )

    @classmethod
    def get_rag_text(cls, search_text):
        from .finetune import add_context_info

        rawqs = cls.get_search_results(search_text)
        rag_text = ""
        for example in rawqs:
            obj = cls.objects.get(id=example.id)
            rag_text += (
                f"Question: {obj.prompt_text}\nAnswer: {add_context_info(obj)}\n##\n"
            )
        return rag_text

    def __str__(self):
        return (
            f"Example created by {self.created_by.username} on {self.created_at.date()}"
        )
