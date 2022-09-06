import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm


def post_fltering(z):
    if z < 10.000:
        return 'Under 10'
    if 11.000 <= z < 20.000:
        return 'Between 11 - 20'
    if 21.000 <= z < 30.000:
        return 'Between 21 - 30'
    if 31.000 <= z < 40.000:
        return 'Between 31 - 40'
    if 41.000 <= z <= 50.000:
        return 'Between 41 - 50'
    return 'Over 50'


def predict_disease(X_new):
    disease = {0: 'COPD', 1: 'Bronchial Asthma', 2: 'Pneumonia', 3: None}

    df = pd.read_csv('data.csv')
    data = df.columns.to_list()
    filtered_data = data[2:30]
    df['Age'] = df['Age'].apply(post_fltering)
    df[filtered_data] = df[filtered_data].apply(lambda x: pd.factorize(x)[0])

    provided_data = data[2:29]
    X = df[provided_data]
    y = df['Disease type']
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)  # default : 75% / 25% train-test split

    dt = DecisionTreeClassifier().fit(X_train, y_train)
    y_new = dt.predict(X_new)
    return disease[y_new[0]]


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect(to='login')

        context = {'form': form}

        return render(request, self.template_name, context)


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


def home(request):
    formElementsA = [
        'Age', 'Gender', 'Cough', 'Srthroat', 'Wheezing', 'Chills', 'Abpain', 'Vomiting', 'Fever',
        'Headache', 'Nausea', 'Tiredness', 'Malaise', 'Bodyache', 'Anorexia',
        'Breathless', 'Convulsion', 'Weightloss', 'Face', 'Fauces', 'Chestpain',
        'Shivering', 'Sweating', 'Shoulderpain', 'HL', 'Asthmatic', 'Dyspnea'
    ]

    formElementsB = [
        'Age', 'Gender', 'Condition of Cough', 'Sore Throat', 'Wheezing', 'Chills', 'Abdominal Pain', 'Vomiting',
        'Fever', 'Headache', 'Nausea', 'Tiredness', 'Malaise', 'Body Ache', 'Anorexia', 'Shortness of Breath',
        'Convulsion', 'Weight Loss', 'Face Condition', 'Fauces Condition', 'Chest Pain', 'Shivering', 'Sweating',
        'Shoulder Pain', 'Herpes Labialis Found', 'Periodic Asthmatic Suffering', 'Nocturnal Episode of Dyspnea']

    formElementsC = [
        ['Under 10', 'Between 11 - 20', 'Between 21 - 30', 'Between 31 - 40', 'Between 41 - 50', 'Over 50'],
        ['Male', 'Female'],
        ['Unproductive', 'Sputum production/ Blood strained (hemoptysis)'],
        ['Yes', 'No'],
        ['High', 'Moderate', 'Low', 'None'],
        ['Yes', 'No'],
        ['High', 'Moderate', 'Low', 'None'],
        ['Yes', 'No'],
        ['< 103 degree', '>= 103 degree', 'none'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['High', 'Moderate', 'Low', 'None'],
        ['High', 'Moderate', 'Low', 'None'],
        ['Yes', 'No'],
        ['Flushed', 'Not flushed'],
        ['Hyperemic', 'Non hyperemic'],
        ['High', 'Medium', 'Low', 'None'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['Yes', 'No'],
        ['< 2 days in a week', '>= 2 days in a week', 'none'],
        ['< 2 days in a month', '> 2 days in a month', 'none']
    ]

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-home')

    elif request.user.is_authenticated:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'formElements': zip(formElementsA, formElementsB, formElementsC)
        }

        return render(request, 'home.html', context)

    return render(request, 'home.html')


def disease_diagnosis_view(request):
    if request.method == 'POST':
        X_new = [[int(request.POST['Age']), int(request.POST['Gender']), int(request.POST['Cough']),
                  int(request.POST['Srthroat']), int(request.POST['Wheezing']), int(request.POST['Chills']),
                  int(request.POST['Abpain']), int(request.POST['Vomiting']), int(request.POST['Fever']),
                  int(request.POST['Headache']), int(request.POST['Nausea']), int(request.POST['Tiredness']),
                  int(request.POST['Malaise']), int(request.POST['Bodyache']), int(request.POST['Anorexia']),
                  int(request.POST['Breathless']), int(request.POST['Convulsion']), int(request.POST['Weightloss']),
                  int(request.POST['Face']), int(request.POST['Fauces']), int(request.POST['Chestpain']),
                  int(request.POST['Shivering']), int(request.POST['Sweating']), int(request.POST['Shoulderpain']),
                  int(request.POST['HL']), int(request.POST['Asthmatic']), int(request.POST['Dyspnea'])]]

        ans = predict_disease(X_new)

        if request.user.is_authenticated:
            user_form = UpdateUserForm(instance=request.user)
            profile_form = UpdateProfileForm(instance=request.user.profile)

            context = {
                'disease': ans,
                'user_form': user_form,
                'profile_form': profile_form
            }

            return render(request, 'appointment.html', context)

    return redirect(to='users-home')


def appointment_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        location = request.POST['location']

        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

        context = {
            'first_name': first_name, 'last_name': last_name, 'email': email,
            'phone': phone, 'date': date, 'location': location,
            'user_form': user_form, 'profile_form': profile_form,
        }

        return render(request, 'doctor.html', context)

    return redirect(to='users-home')
