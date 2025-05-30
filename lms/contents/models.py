from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subjects',
        null=True,
        blank=True
    )
    students = models.ManyToManyField(
        User,
        related_name='subjects_enrolled',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.teacher and not self.teacher.is_teacher:
            raise ValidationError("Assigned teacher must have is_teacher=True.")

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name_plural = 'Subjects'



class Topic(models.Model):
    topic_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.teacher and not self.teacher.is_teacher:
            raise ValidationError("Assigned teacher must have is_teacher=True.")

    def __str__(self):
        return f"{self.topic_name} ({self.subject.subject_name})"

    class Meta:
        ordering = ['topic_name']
        verbose_name_plural = 'Topics'

class Content(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ManyToManyField(
        User,
        related_name='assigned_contents',
        blank=True
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        related_name='contents',
        null=True,
        blank=True
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='contents'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contents'

def content_file_upload_path(instance, filename):
    if instance.content and instance.content.pk:
        return f'contents/{instance.content.pk}/{filename}'
    return f'contents/temp/{uuid.uuid4()}/{filename}'


class ContentFile(models.Model):
    FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('ppt', 'PowerPoint'),
        ('doc', 'Word Doc'),
        ('docx', 'Word Docx'),
        ('pdf', 'PDF'),
        ('other', 'Other'),
    ]

    file = models.FileField(upload_to=content_file_upload_path)
    mime_type = models.CharField(max_length=20, choices=FILE_TYPES)
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='files'
    )

    def __str__(self):
        return f"{self.mime_type} for {self.content.title}"

    class Meta:
        verbose_name_plural = 'Content Files'

class ContentLink(models.Model):
    link = models.URLField()
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='links'
    )

    def __str__(self):
        return f"Link for {self.content.title}"

    class Meta:
        verbose_name_plural = 'Content Links'
