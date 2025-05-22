from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .models import Question, Tag, Answer, Profile, User, QuestionLike, AnswerLike
from django.db.models import Count


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    total_pages = paginator.num_pages
    current_page = page.number
    max_pages = 5

    start_page = max(1, current_page - max_pages // 2)
    end_page = min(total_pages, start_page + max_pages - 1)

    if end_page - start_page < max_pages - 1:
        start_page = max(1, end_page - max_pages + 1)

    page_range = range(start_page, end_page + 1)

    return page, page_range


def new_questions(request):
    questions = Question.objects.new()
    page, page_range = paginate(questions, request)

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'new_questions.html', {
        'questions': page.object_list,
        'page_obj': page,
        'page_range': page_range,
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def hot_questions(request):
    questions = Question.objects.best()
    page, page_range = paginate(questions, request)

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'hot_questions.html', {
        'questions': page.object_list,
        'page_obj': page,
        'page_range': page_range,
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(question=question).order_by('-is_correct', '-created_at')

    page, page_range = paginate(answers, request, per_page=5)

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'question.html', {
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
        'page_range': page_range,
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page, page_range = paginate(questions, request)

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'tag.html', {
        'tag': tag,
        'questions': page.object_list,
        'page_obj': page,
        'page_range': page_range,
        'popular_tags': popular_tags,
        'best_members': best_members
    })


@login_required(login_url='/login/')
def ask(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        tags_str = request.POST.get('tags', '')
        
        if not title or not text:
            messages.error(request, 'Пожалуйста, заполните все обязательные поля')
            return render(request, 'ask.html', {
                'popular_tags': popular_tags,
                'best_members': best_members
            })

        profile = Profile.objects.get(user=request.user)
        question = Question.objects.create(title=title, text=text, author=profile)

        tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)

        messages.success(request, 'Вопрос успешно создан!')
        return redirect('question', question_id=question.id)

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'ask.html', {
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('new_questions')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'login.html', {
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)

        messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
        return redirect('login')

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'signup.html', {
        'popular_tags': popular_tags,
        'best_members': best_members
    })


def logout(request):
    auth_logout(request)
    return redirect('new_questions')


@login_required
def settings(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile = user.profile
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()

        messages.success(request, 'Настройки успешно обновлены!')
        return redirect('settings')

    popular_tags = Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]
    best_members = Profile.objects.annotate(num_answers=Count('answer')).order_by('-num_answers')[:5]

    return render(request, 'settings.html', {
        'popular_tags': popular_tags,
        'best_members': best_members,
        'user': request.user
    })


@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user.profile,
        question=question,
        defaults={'value': 1}
    )
    if not created:
        if like.value == 1:
            like.delete()
        else:
            like.value = 1
            like.save()

    return redirect('question', question_id=question_id)


@login_required
def dislike_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user.profile,
        question=question,
        defaults={'value': -1}
    )
    if not created:
        if like.value == -1:
            like.delete()
        else:
            like.value = -1
            like.save()

    return redirect('question', question_id=question_id)


@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user.profile,
        answer=answer,
        defaults={'value': 1}
    )
    if not created:
        if like.value == 1:
            like.delete()
        else:
            like.value = 1
            like.save()

    return redirect('question', question_id=answer.question.id)


@login_required
def dislike_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    like, created = AnswerLike.objects.get_or_create(
        user=request.user.profile,
        answer=answer,
        defaults={'value': -1}
    )
    if not created:
        if like.value == -1:
            like.delete()
        else:
            like.value = -1
            like.save()

    return redirect('question', question_id=answer.question.id)