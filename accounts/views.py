from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import SignUpForm

# Create your views here.


# def custom_login_view(request, *args, **kwargs):
#     if request.method == 'POST':
#         form = AuthenticationForm(request.POST)
#         if form.is_valid():
#             raw_password = form.cleaned_data.get('password1')
#             username = form.cleaned_data.get('username')
#             user = authenticate(username=username, password=raw_password)
#             if user is not None:
#                 login(request, user)
#                 # Redirect to a success page.
#                 return redirect('workflow:home')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})


def profile_view(request):
    return render(request, 'accounts/profile.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            #user.profile.address = form.cleaned_data.get('address')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            return redirect('accounts:profile')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view.
    """

    form_class = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        return super(CustomLoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        if 'remember_me' not in form.data:
            print('Remember_me is OFF!')
            self.request.session.set_expiry(0)
        else:
            print(form.data['remember_me'])
            self.request.session.set_expiry(36000)

        return super(CustomLoginView, self).form_valid(form)
