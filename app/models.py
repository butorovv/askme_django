from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')
    
    def best(self):
        return self.annotate(total_likes=Count('questionlike')).order_by('-total_likes')
    
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
        return self.questionlike_set.count()
    
    def answers_count(self):
        return self.answer_set.count()


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


class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(default=1)  # 1 for like, -1 for dislike
    
    class Meta:
        unique_together = ('user', 'question')
    
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
    
    def __str__(self):
        return f"{self.user.user.username} {'likes' if self.value > 0 else 'dislikes'} answer to {self.answer.question.title}"
    
    def save(self, *args, **kwargs):
        if abs(self.value) != 1:
            raise ValidationError("Value must be either 1 (like) or -1 (dislike)")
        super().save(*args, **kwargs)