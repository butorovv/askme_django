from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import redirect
def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page, paginator

def new_questions(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Вопрос {i}',
            'text': f'Текст вопроса {i}',
            'answers_count': i % 5,  # Единообразие именования
            'rating': i * 2 % 10,   # Добавили рейтинг
            'tags': [{'name': 'new'}, {'name': 'django'}],  # Добавили теги
            'author': {'username': f'User{i}', 'avatar_url': '/static/images/avatar.jpg'}
        })
    
    # Сортировка по новизне (обратный порядок)
    questions = sorted(questions, key=lambda x: x['id'], reverse=True)
    
    page, paginator = paginate(questions, request)
    
    return render(request, 'new_questions.html', {
        'questions': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'popular_tags': [{'name': 'django'}, {'name': 'python'}],
        'best_members': [{'username': 'User1'}, {'username': 'User2'}]
    })

def hot_questions(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Популярный вопрос {i}',
            'text': f'Текст популярного вопроса {i}',
            'answers_count': i % 5,
            'rating': i * 3 % 10,
            'tags': [{'name': 'popular'}, {'name': 'hot'}],
            'author': {'username': f'HotUser{i}', 'avatar_url': '/static/images/avatar.jpg'}
        })
    
    # Сортировка по рейтингу
    questions = sorted(questions, key=lambda x: x['rating'], reverse=True)
    
    page, paginator = paginate(questions, request)
    
    return render(request, 'hot_questions.html', {
        'questions': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'popular_tags': [{'name': 'popular'}, {'name': 'hot'}],
        'best_members': [{'username': 'User1'}, {'username': 'User2'}]
    })

def question(request, question_id):
    # Пример данных - замените на реальную логику
    question_data = {
        'id': question_id,
        'title': f'Вопрос {question_id}',
        'text': f'Полный текст вопроса {question_id}',
        'answers_count': 3,
        'rating': 5,
        'tags': [{'name': 'django'}, {'name': 'python'}]
    }
    
    return render(request, 'question.html', {
        'question': question_data,
        'popular_tags': [{'name': 'django'}, {'name': 'python'}],
        'best_members': [{'username': 'Expert1'}, {'username': 'Expert2'}]
    })

def tag(request, tag_name):  # Исправьте параметр на tag_name
    questions = []
    for i in range(1, 15):
        questions.append({
            'title': f'Вопрос с тегом {tag_name} {i}',  
            'id': i,
            'text': f'Текст вопроса с тегом {tag_name} {i}', 
            'answers': i % 5,
            'tags': [
                {'name': tag_name},
                {'name': 'related'},
            ]
        })

    popular_tags = [
        {'name': tag_name}, 
        {'name': 'django'}, 
        {'name': 'web'},
        {'name': 'html'},
        {'name': 'css'}
    ]
    
    best_members = [
        {'username': 'MrButorov'},
        {'username': 'Alice'},
        {'username': 'Bob'},
        {'username': 'Charlie'}
    ]

    page, paginator = paginate(questions, request)

    return render(request, 'tag.html', {
        'tag': tag_name,
        'questions': page.object_list,
        'page_obj': page,
        'paginator': paginator,
        'popular_tags': popular_tags,
        'best_members': best_members
    })

def ask(request):
    popular_tags = [
        {'name': 'python'}, 
        {'name': 'django'}, 
        {'name': 'web'}
    ]
    
    best_members = [
        {'username': 'Helper1'},
        {'username': 'Helper2'}
    ]
    
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
            messages.error(request, 'Invalid username or password')
    
    popular_tags = [
        {'name': 'python'}, 
        {'name': 'django'}, 
        {'name': 'web'}
    ]
    
    best_members = [
        {'username': 'User1'},
        {'username': 'User2'}
    ]
    
    return render(request, 'login.html', {
        'popular_tags': popular_tags,
        'best_members': best_members
    })

def signup(request):
    if request.method == 'POST':
        # Здесь должна быть логика регистрации
        # Например, создание нового пользователя
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')
    
    popular_tags = [
        {'name': 'python'}, 
        {'name': 'django'}, 
        {'name': 'web'}
    ]
    
    best_members = [
        {'username': 'NewUser1'},
        {'username': 'NewUser2'}
    ]
    
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
        # Здесь должна быть логика обновления профиля
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    popular_tags = [
        {'name': 'python'}, 
        {'name': 'django'}, 
        {'name': 'web'}
    ]
    
    best_members = [
        {'username': 'TopUser1'},
        {'username': 'TopUser2'}
    ]
    
    return render(request, 'settings.html', {
        'popular_tags': popular_tags,
        'best_members': best_members,
        'user': request.user  # Передаем текущего пользователя
    })