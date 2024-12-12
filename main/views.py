from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, AptitudeTest
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
import io
import urllib, base64
import numpy as np

def home(request):
    return render(request, 'main/home.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'main/login.html', {'error': 'Invalid credentials'})
    return render(request, 'main/login.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def dashboard(request):
    if request.method == 'POST':
        domain = request.POST['domain']
        profile = Profile.objects.get(user=request.user)
        profile.domain = domain
        profile.save()
        return redirect('careers')  # Ensure this URL pattern exists or change to a valid one
    return render(request, 'main/dashboard.html')

def aptitude_test(request):
    questions = [
        "What is the capital of France?",
        "What is 2 + 2?",
        "Who wrote 'To Kill a Mockingbird'?",
        "What is the powerhouse of the cell?",
        # Add more questions as needed
    ]
    correct_answers = [
        "Paris",
        "4",
        "Harper Lee",
        "Mitochondria",
        # Add corresponding correct answers
    ]
    domains = [
        "General Knowledge",
        "Math",
        "Literature",
        "Biology",
        # Add corresponding domains
    ]

    # Initialize the score dictionary for all possible domains
    score = {'General Knowledge': 0, 'Math': 0, 'Literature': 0, 'Biology': 0}

    if request.method == 'POST':
        for i, question in enumerate(questions):
            user_answer = request.POST.get(f'question_{i}')
            AptitudeTest.objects.create(
                user=request.user,
                question=question,
                domain=domains[i],
                answer=correct_answers[i],
                user_answer=user_answer
            )
            if user_answer == correct_answers[i]:
                score[domains[i]] += 1

        # KNN training data (example)
        training_scores = [
            [10, 0, 0, 0],  # General Knowledge
            [0, 10, 0, 0],  # Math
            [0, 0, 10, 0],  # Literature
            [0, 0, 0, 10],  # Biology
            # Add more training examples
        ]
        training_labels = ["General Knowledge", "Math", "Literature", "Biology"]

        # Train KNN model
        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(training_scores, training_labels)

        # Predict domain
        user_scores = [score['General Knowledge'], score['Math'], score['Literature'], score['Biology']]
        predicted_domain = knn.predict([user_scores])[0]

        profile = Profile.objects.get(user=request.user)
        profile.domain = predicted_domain
        profile.save()

        request.session['score'] = score
        request.session['domain'] = predicted_domain

        return redirect('result')

    return render(request, 'main/aptitude_test.html', {'questions': questions})

def result(request):
    score = request.session.get('score', {})
    domain = request.session.get('domain', '')

    if not score:
        return redirect('aptitude_test')

    labels = list(score.keys())
    sizes = list(score.values())
    colors = plt.cm.Paired(range(len(labels)))  # Using a colormap for better color diversity

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    ax.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'main/result.html', {'data': uri, 'domain': domain})

def careers(request):
    profile = Profile.objects.get(user=request.user)
    domain = profile.domain
    # Define careers based on the domain
    careers = {
        'Science': ['Engineer: https://engineering.careers360.com/articles/list-of-engineering-courses-after-12th', 'Doctor', 'Scientist'],
        'Commerce': ['Accountant', 'Business Analyst', 'Economist'],
        'Arts': ['Artist', 'Writer', 'Historian'],
    }
    return render(request, 'main/careers.html', {'careers': careers.get(domain, [])})
