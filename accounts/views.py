from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import resolve, reverse, Resolver404, NoReverseMatch
from django.http import HttpResponseRedirect
from django.contrib import messages
from urllib.parse import urlparse
from .forms import SignUpForm, ProfileEditForm


def _get_safe_redirect(request):
    """
    Return a safe internal redirect URL from the 'next' GET parameter,
    or None if the URL is invalid or external.
    The taint chain is broken by reconstructing the URL via reverse().
    """
    next_url = request.GET.get(REDIRECT_FIELD_NAME, '')
    if not next_url:
        return None
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return None
    path = urlparse(next_url).path
    try:
        match = resolve(path)
        # Reconstruct from the URL pattern registry — breaks the user-input taint chain
        clean_url = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
        return clean_url
    except (Resolver404, NoReverseMatch):
        return None


class BootstrapAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = BootstrapAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'{user.username}님 환영합니다!')
            clean_url = _get_safe_redirect(request)
            if clean_url:
                return HttpResponseRedirect(clean_url)
            return redirect('home')
    else:
        form = BootstrapAuthForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '로그아웃 되었습니다.')
    return redirect('home')


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '회원정보가 수정되었습니다.')
            return redirect('home')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})
