import json
from collections import Counter
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from search.forms import UserLoginForm, UserRegistrationForm
from search.models import SearchHistory

yesterday = date.today() - timedelta(days=1)
last_week = date.today() - timedelta(days=7)
last_month = date.today().replace(day=1)


def search(request):
    if request.method == "GET":
        key = request.GET['search']
        # url = f'https://www.bing.com/search?q={key}'
        url = f'https://www.ask.com/web?q={key}'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        result = soup.find_all(attrs={"class": "PartialSearchResults-item"})
        if result:
            resultStr = ' '.join([str(r) for r in result])
            search_history = SearchHistory(keyword=key, result=resultStr, user=request.user)
            search_history.save()
            # content = []
            # for li in result:
            #     content2 = [str(li.find('h2')), str(li.find(class_='b_caption'))]
            # content.append(content2)
            return render(request, template_name='index.html', context={'content': resultStr})
    return render(request, template_name='index.html')


def index(request):
    # get all SearchHistory by reverse order
    search_history = SearchHistory.objects.all().order_by("-id")
    # get all keywords
    key_w = search_history.values_list('keyword', flat=True).distinct()
    # count keywords as (key, value) pair
    keywords = dict(Counter(list(key_w)))
    username_list = list(User.objects.all().values_list('username', flat=True).distinct())
    if request.method == "GET":

        content = []
        for sh in search_history:
            content.append([sh.keyword, sh.result, sh.user])
        if not request.user.is_authenticated:
            return render(request, template_name='index.html',
                          context={"username_list": username_list, 'keywords': keywords, 'content': content})
        return render(request, template_name='index.html')
    if request.method == "POST":
        kw = request.POST.get('keyword')
        data = json.loads(request.body.decode("utf-8"))
        content = []
        # filter section
        if data:
            if data["keyword"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']))
            if data["username"]:
                search_history = search_history.filter(
                    Q(user__username__in=data['username']))
            if data["yesterday"]:
                search_history = search_history.filter(
                    datetime__gte=yesterday)
            if data["last_week"]:
                search_history = search_history.filter(
                    datetime__gte=last_week)
            if data["last_month"]:
                search_history = search_history.filter(
                    datetime__gte=last_month)
            if data["start_date"]:
                search_history = search_history.filter(
                    datetime__gte=data["start_date"])
            if data["end_date"]:
                search_history = search_history.filter(
                    datetime__lte=data["end_date"])
            if data["start_date"] and data["username"]:
                search_history = search_history.filter(
                    datetime__range=(data['start_date'], data['end_date']))
            if data["keyword"] and data["username"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']) & Q(user__username__in=data['username']))
            if data["keyword"] and data["username"] and data["yesterday"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']) & Q(user__username__in=data['username']) &
                    Q(datetime__gte=data["yesterday"]))
            if data["keyword"] and data["username"] and data["last_week"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']) & Q(user__username__in=data['username']) &
                    Q(datetime__gte=data["last_week"]))
            if data["keyword"] and data["username"] and data["last_month"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']) & Q(user__username__in=data['username']) &
                    Q(datetime__gte=data["last_month"]))
            if data["keyword"] and data["username"] and data["start_date"] and data["end_date"]:
                search_history = search_history.filter(
                    Q(keyword__in=data['keyword']) & Q(user__username__in=data['username']) &
                    Q(datetime__range=(data['start_date'], data['end_date'])))
            for sh in search_history:
                print(sh.keyword)
                content.append([sh.keyword, sh.result, sh.user.username])

            # return render(request, template_name='index.html', context={'content': content})
            return JsonResponse({'content': content})
        return render(request, template_name='index.html')


def login_attempt(request):
    _next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            if _next:
                return redirect(_next)
            return redirect('Index')
        return render(request, 'login.html', {'form': form})
    return render(request, 'login.html', {'form': form})


def logout_attempt(request):
    logout(request)
    return redirect('Index')


def register_attempt(request):
    form = UserRegistrationForm(request.POST or None)
    login_form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return render(request, 'login.html', {'form': login_form})
        return render(request, 'register.html', {'form': form})
    return render(request, 'register.html', {'form': form})
