from django.shortcuts import render,redirect
from .models import Food,Consume
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
def index(request):
    if request.method=="POST":
        food_consumed=request.POST['food_consumed']
        consume=Food.objects.get(name=food_consumed)
        user=request.user
        consume=Consume(user=user,food_consumed=consume)
        consume.save()
        foods = Food.objects.all()
    else:
    
        foods=Food.objects.all()
    consumed_food=Consume.objects.filter(user=request.user)
    return render(request,"myapp/index.html",{'foods':foods,'consumed_food':consumed_food})
def delete_consume(request,id):
    consumed_food = Consume.objects.get(id=id)
    if request.method =='POST':
        consumed_food.delete()
        return redirect('/')
    return render(request,'myapp/delete.html')
def home(request):
    return render(request, 'myapp/home.html')


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})