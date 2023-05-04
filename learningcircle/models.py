from django.db import models


class LearningCircle(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    circle_code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True, blank=False)
    password = models.CharField(max_length=255)
    interest_group_id = models.CharField(max_length=36, null=False)
    college_id = models.CharField(max_length=36, null=False)
    lead_id = models.CharField(max_length=36, null=False)
    meet_place = models.CharField(max_length=255)
    meet_time = models.TimeField()
    updated_by = models.CharField(max_length=36)
    updated_at = models.DateTimeField()
    created_by = models.CharField(max_length=36)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "learning_circle"


class CircleUserLink(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    circle = models.ForeignKey(LearningCircle, models.DO_NOTHING)
    user_id = models.CharField(max_length=36)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(default=None)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.circle.name

    class Meta:
        managed = False
        db_table = "user_circle_link"
