from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
import random
from faker import Faker
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Fills the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio for filling the database')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fake = Faker()

        self.stdout.write(self.style.SUCCESS('Step 1: Creating users...'))
        users = []
        for i in tqdm(range(ratio), total=ratio, desc="Users"):
            username = f"user{i}"
            email = f"user{i}@example.com"
            password = "password123"

            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                users.append(user.profile)
                continue

            user = User.objects.create_user(username=username, email=email, password=password)
            profile = Profile.objects.create(user=user)
            users.append(profile)

        self.stdout.write(self.style.SUCCESS(f'Created or reused {len(users)} users'))

        self.stdout.write(self.style.SUCCESS('Step 2: Creating tags...'))
        tags = []
        for i in tqdm(range(ratio), total=ratio, desc="Tags"):
            tag_name = f"tag{i}"
            if Tag.objects.filter(name=tag_name).exists():
                tags.append(Tag.objects.get(name=tag_name))
                continue

            tag = Tag.objects.create(name=tag_name)
            tags.append(tag)

        self.stdout.write(self.style.SUCCESS(f'Created or reused {len(tags)} tags'))

        self.stdout.write(self.style.SUCCESS('Step 3: Creating questions...'))
        questions = []
        for i in tqdm(range(ratio * 10), total=ratio * 10, desc="Questions"):
            author = random.choice(users)
            question = Question.objects.create(
                title=fake.sentence(nb_words=6),
                text=fake.paragraph(nb_sentences=5),
                author=author
            )
            num_tags = random.randint(1, 3)
            selected_tags = random.sample(tags, num_tags)
            question.tags.add(*selected_tags)
            questions.append(question)

        self.stdout.write(self.style.SUCCESS(f'Created {len(questions)} questions'))

        self.stdout.write(self.style.SUCCESS('Step 4: Creating answers...'))
        answers = []
        for i in tqdm(range(ratio * 100), total=ratio * 100, desc="Answers"):
            question = random.choice(questions)
            author = random.choice(users)
            answer = Answer.objects.create(
                text=fake.paragraph(nb_sentences=3),
                author=author,
                question=question
            )
            answers.append(answer)

        self.stdout.write(self.style.SUCCESS(f'Created {len(answers)} answers'))

        self.stdout.write(self.style.SUCCESS('Step 5: Adding likes to questions...'))
        for question in tqdm(questions, total=len(questions), desc="Question Likes"):
            liked_profiles = random.sample(users, random.randint(0, len(users)))
            for profile in liked_profiles:
                value = random.choice([1, -1])
                QuestionLike.objects.get_or_create(
                    user=profile,
                    question=question,
                    defaults={'value': value}
                )
                
        self.stdout.write(self.style.SUCCESS('Step 6: Adding likes to answers...'))
        for answer in tqdm(answers, total=len(answers), desc="Answer Likes"):
            liked_profiles = random.sample(users, random.randint(0, len(users)))
            for profile in liked_profiles:
                value = random.choice([1, -1])
                AnswerLike.objects.get_or_create(
                    user=profile,
                    answer=answer,
                    defaults={'value': value}
                )

        self.stdout.write(self.style.SUCCESS('✅ Successfully filled the database with test data!'))