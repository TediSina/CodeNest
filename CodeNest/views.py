from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserChangeForm
from forum.models import Question, Answer

@login_required
def profile_view(request):
    user_questions = Question.objects.filter(author=request.user).order_by('-created_at')
    user_answers = Answer.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'profile.html', {
        'user': request.user,
        'questions': user_questions,   
        'answers': user_answers
    })

@login_required
def edit_profile_view(request):
    profile_form = CustomUserChangeForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'profile_submit' in request.POST:
            profile_form = CustomUserChangeForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been successfully updated!')
                return redirect('profile')

        elif 'password_submit' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Your password has been successfully updated!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors in the password form.')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'edit_profile.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
