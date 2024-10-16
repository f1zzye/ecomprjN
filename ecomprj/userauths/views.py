from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User, Profile
from userauths.forms import User, ProfileForm


def register_view(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect('core:index')


    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'userauths/sign-up.html', context)


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f'You are already logged in.')
        return redirect('core:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.mfa_enabled:
                    return render(request, 'userauths/otp_verify.html', {'user_id': user.id})
                login(request, user)
                messages.success(request, f'Welcome {user.username}')
                return redirect('core:index')
            else:
                messages.warning(request, 'User Does Not Exist, create an account.')
        except User.DoesNotExist:
            messages.warning(request, f'User with {email} does not exist')

    return render(request, 'userauths/sign-in.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You logged out.')
    return redirect('userauths:sign-in')


def profile_edit(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('core:dashboard')
        else:
            form = ProfileForm()

    form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'userauths/profile-edit.html', context)




