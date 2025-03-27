from django.shortcuts import render, redirect
from .models import Food, Consume
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
import random
from datetime import timedelta

# Function to generate meal suggestions based on calorie goal
def generate_meal_plan(calorie_goal):
    foods = list(Food.objects.all())
    meal_plan = []
    total_calories = 0

    random.shuffle(foods)
    for food in foods:
        if (total_calories + food.calories) <= calorie_goal:
            meal_plan.append(food)
            total_calories += food.calories
        if total_calories >= calorie_goal:
            break

    return meal_plan, total_calories


def index(request):
    # Handle calorie goal setting
    if 'calorie_goal' in request.POST:
        calorie_goal = request.POST.get('calorie_goal')
        if calorie_goal:
            request.session['calorie_goal'] = int(calorie_goal)
    
    # Retrieve calorie goal from session
    calorie_goal = request.session.get('calorie_goal', 2000)
    
    # Handle food consumption
    if request.method == "POST" and 'food_consumed' in request.POST:
        food_consumed = request.POST['food_consumed']
        consume = Food.objects.get(name=food_consumed)
        user = request.user
        consume = Consume(user=user, food_consumed=consume)
        consume.save()

    # Handle meal plan generation
    meal_plan = []
    total_meal_calories = 0
    if 'generate_meal_plan' in request.POST:
        meal_plan, total_meal_calories = generate_meal_plan(calorie_goal)
        request.session['meal_plan'] = [food.name for food in meal_plan]
        request.session['total_meal_calories'] = total_meal_calories
    
    # Retrieve meal plan and total calories from session
    meal_plan_names = request.session.get('meal_plan', [])
    total_meal_calories = request.session.get('total_meal_calories', 0)
    meal_plan = Food.objects.filter(name__in=meal_plan_names)
    
    # Retrieve data for the template
    foods = Food.objects.all()
    consumed_food = Consume.objects.filter(user=request.user)
    
    # Pass calorie goal and meal plan to template
    context = {
        'foods': foods,
        'consumed_food': consumed_food,
        'calorie_goal': calorie_goal,
        'meal_plan': meal_plan,
        'total_meal_calories': total_meal_calories,
    }
    
    return render(request, "myapp/index.html", context)


def delete_consume(request, id):
    consumed_food = Consume.objects.get(id=id)
    if request.method == 'POST':
        consumed_food.delete()
        return redirect('/')
    return render(request, 'myapp/delete.html')


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


def get_date_range(days):
    today = timezone.now()
    start_date = today - timedelta(days=days)
    return start_date, today


# Weekly Report View
def weekly_report(request):
    start_date, end_date = get_date_range(7)
    create_test_data()

    # Create test data (run this ONCE for testing)
    food = Food.objects.first()
    if not food:
        return render(request, "myapp/weekly_report.html", {"error": "No food items found."})
    
    # Simulate past dates for testing (if needed)
    if not Consume.objects.filter(user=request.user, date__range=[start_date, end_date]).exists():
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now())
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now() - timedelta(days=3))
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now() - timedelta(days=6))

    consumed = Consume.objects.filter(user=request.user, date__range=[start_date, end_date])

    total_calories = sum(item.food_consumed.calories for item in consumed)
    total_carbs = sum(item.food_consumed.carbs for item in consumed)
    total_proteins = sum(item.food_consumed.proteins for item in consumed)
    total_fats = sum(item.food_consumed.fats for item in consumed)
    total_meals = consumed.count()

    context = {
        'weekly_data': consumed,
        'total_weekly_calories': total_calories,
        'total_weekly_carbs': total_carbs,
        'total_weekly_proteins': total_proteins,
        'total_weekly_fats': total_fats,
        'total_meals': total_meals,
    }
    return render(request, "myapp/weekly_report.html", context)


# Monthly Report View
def monthly_report(request):
    start_date, end_date = get_date_range(30)

    # Create test data (run this ONCE for testing)
    food = Food.objects.first()
    if not food:
        return render(request, "myapp/monthly_report.html", {"error": "No food items found."})

    # Simulate past dates for testing (if needed)
    if not Consume.objects.filter(user=request.user, date__range=[start_date, end_date]).exists():
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now() - timedelta(days=10))
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now() - timedelta(days=20))
        Consume.objects.create(user=request.user, food_consumed=food, date=timezone.now() - timedelta(days=29))

    consumed = Consume.objects.filter(user=request.user, date__range=[start_date, end_date])

    total_calories = sum(item.food_consumed.calories for item in consumed)
    total_carbs = sum(item.food_consumed.carbs for item in consumed)
    total_proteins = sum(item.food_consumed.proteins for item in consumed)
    total_fats = sum(item.food_consumed.fats for item in consumed)
    total_meals = consumed.count()

    context = {
        'monthly_data': consumed,
        'total_monthly_calories': total_calories,
        'total_monthly_carbs': total_carbs,
        'total_monthly_proteins': total_proteins,
        'total_monthly_fats': total_fats,
        'total_meals': total_meals,
    }
    return render(request, "myapp/monthly_report.html", context)
def create_test_data():
    user = User.objects.first()  # Get the first user
    food = Food.objects.first()  # Get the first food item

    if user and food:
        Consume.objects.create(user=user, food_consumed=food, date=timezone.now())
        Consume.objects.create(user=user, food_consumed=food, date=timezone.now() - timedelta(days=1))
        Consume.objects.create(user=user, food_consumed=food, date=timezone.now() - timedelta(days=2))
        Consume.objects.create(user=user, food_consumed=food, date=timezone.now() - timedelta(days=3))
        Consume.objects.create(user=user, food_consumed=food, date=timezone.now() - timedelta(days=5))
