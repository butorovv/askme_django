from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    objects = models.Manager()
    
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Profiles"
        ordering = ['-id']


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tags"
        ordering = ['name']


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')
    
    def best(self):
        return self.annotate(likes_count=Count('questionlike')).order_by('-likes_count', '-created_at')
    
    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name)


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return f'/question/{self.id}/'
    def likes_count(self):
        return self.questionlike_set.filter(value=1).count()
    def dislikes_count(self):
        return self.questionlike_set.filter(value=-1).count()
    def answers_count(self):
        return self.answer_set.count()
    

    class Meta:
        verbose_name_plural = "Questions"
        ordering = ['-created_at']


class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    def likes_count(self):
        return self.answerlike_set.count()

    class Meta:
        verbose_name_plural = "Answers"
        ordering = ['-is_correct', '-created_at']


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=1)  # 1 for like, -1 for dislike
    
    class Meta:
        unique_together = ('user', 'question')
        verbose_name_plural = "Question Likes"
    
    def __str__(self):
        return f"{self.user.user.username} {'likes' if self.value > 0 else 'dislikes'} {self.question.title}"
    
    def save(self, *args, **kwargs):
        if abs(self.value) != 1:
            raise ValidationError("Value must be either 1 (like) or -1 (dislike)")
        super().save(*args, **kwargs)


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=1)  # 1 for like, -1 for dislike
    
    class Meta:
        unique_together = ('user', 'answer')
        verbose_name_plural = "Answer Likes"
    
    def __str__(self):
        return f"{self.user.user.username} {'likes' if self.value > 0 else 'dislikes'} answer to {self.answer.question.title}"
    
    def save(self, *args, **kwargs):
        if abs(self.value) != 1:
            raise ValidationError("Value must be either 1 (like) or -1 (dislike)")
        super().save(*args, **kwargs)