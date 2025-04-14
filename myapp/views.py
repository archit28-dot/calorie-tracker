from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import Food, Consume, CalorieGoal
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.db.models import Q


def food_search(request):
    query = request.GET.get("q", "")

    if query:
        foods = Food.objects.filter(
            Q(name__icontains=query)
            | Q(name__icontains=query.replace("(", "").replace(")", ""))
        )[
            :5
        ]  # Limit to 5 suggestions
        results = [
            {
                "name": food.name,
                "id": food.id,
                "carbs": food.carbs_per_100g,
                "proteins": food.proteins_per_100g,
                "fats": food.fats_per_100g,
            }
            for food in foods
        ]
    else:
        results = []

    return JsonResponse({"results": results})


def index(request):
    # Handle date selection from calendar
    if "selected_date" in request.GET:
        selected_date = request.GET["selected_date"]
        try:
            datetime.strptime(selected_date, "%Y-%m-%d").date()
            return HttpResponseRedirect(
                reverse("date_log", kwargs={"selected_date": selected_date})
            )
        except ValueError:
            messages.error(request, "Invalid date format")

    # Handle calorie goal setting
    if "calorie_goal" in request.POST:
        calorie_goal = request.POST.get("calorie_goal")
        if calorie_goal:
            calorie_goal = int(calorie_goal)
            request.session["calorie_goal"] = calorie_goal
            if request.user.is_authenticated:
                CalorieGoal.objects.update_or_create(
                    user=request.user,
                    date=timezone.now().date(),
                    defaults={"calorie_goal": calorie_goal},
                )

    # Retrieve calorie goal
    if request.user.is_authenticated and hasattr(request.user, "caloriegoal"):
        calorie_goal = request.user.caloriegoal.calorie_goal
    else:
        calorie_goal = request.session.get("calorie_goal", 2000)

    # Handle food consumption
    if request.method == "POST" and "food_consumed" in request.POST:
        food_consumed_id = request.POST["food_consumed"]
        quantity_consumed = float(request.POST.get("quantity_consumed", 100))
        consume_food = Food.objects.get(id=food_consumed_id)
        if request.user.is_authenticated:
            Consume.objects.create(
                user=request.user,
                food_consumed=consume_food,
                quantity_consumed=quantity_consumed,
                date=timezone.now().date(),
            )

    # Generate meal plan

    # Get all foods and consumed items
    foods = Food.objects.all()
    consumed_food = (
        Consume.objects.filter(user=request.user, date=timezone.now().date())
        if request.user.is_authenticated
        else []
    )

    # Calculate totals
    total_calories = sum(item.total_calories for item in consumed_food)
    total_carbs = sum(item.total_carbs for item in consumed_food)
    total_proteins = sum(item.total_proteins for item in consumed_food)
    total_fats = sum(item.total_fats for item in consumed_food)

    context = {
        "foods": foods,
        "consumed_food": consumed_food,
        "calorie_goal": calorie_goal,
        "calories": total_calories,
        "carbs": total_carbs,
        "proteins": total_proteins,
        "fats": total_fats,
        "progress": (total_calories / calorie_goal * 100) if calorie_goal else 0,
        "selected_date": timezone.now().date(),
        "timezone": timezone,
    }

    return render(request, "myapp/index.html", context)


def date_specific_log(request, selected_date):
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Invalid date format")
        return redirect("index")

    # Handle navigation
    day = request.GET.get("day")
    if day == "prev":
        selected_date = selected_date - timedelta(days=1)
        return redirect("date_log", selected_date=selected_date.strftime("%Y-%m-%d"))
    elif day == "next":
        selected_date = selected_date + timedelta(days=1)
        return redirect("date_log", selected_date=selected_date.strftime("%Y-%m-%d"))

    # Handle food consumption
    if request.method == "POST" and "food_consumed" in request.POST:
        food_consumed_id = request.POST["food_consumed"]
        quantity_consumed = float(request.POST.get("quantity_consumed", 100))
        consume_food = Food.objects.get(id=food_consumed_id)
        Consume.objects.create(
            user=request.user,
            food_consumed=consume_food,
            quantity_consumed=quantity_consumed,
            date=selected_date,
        )
        messages.success(request, "Food item added successfully!")
        return redirect("date_log", selected_date=selected_date.strftime("%Y-%m-%d"))

    # Handle calorie goal
    if "calorie_goal" in request.POST:
        calorie_goal = request.POST.get("calorie_goal")
        if calorie_goal:
            calorie_goal = int(calorie_goal)
            CalorieGoal.objects.update_or_create(
                user=request.user,
                date=selected_date,
                defaults={"calorie_goal": calorie_goal},
            )
            messages.success(request, "Calorie goal set successfully!")
            return redirect(
                "date_log", selected_date=selected_date.strftime("%Y-%m-%d")
            )

    # Get data for the selected date
    foods = Food.objects.all()
    consumed_food = Consume.objects.filter(user=request.user, date=selected_date)

    try:
        calorie_goal = CalorieGoal.objects.get(
            user=request.user, date=selected_date
        ).calorie_goal
    except CalorieGoal.DoesNotExist:
        calorie_goal = 2000

    # Calculate totals
    total_calories = sum(item.total_calories for item in consumed_food)
    total_carbs = sum(item.total_carbs for item in consumed_food)
    total_proteins = sum(item.total_proteins for item in consumed_food)
    total_fats = sum(item.total_fats for item in consumed_food)

    context = {
        "foods": foods,
        "consumed_food": consumed_food,
        "calorie_goal": calorie_goal,
        "calories": total_calories,
        "carbs": total_carbs,
        "proteins": total_proteins,
        "fats": total_fats,
        "progress": (total_calories / calorie_goal * 100) if calorie_goal else 0,
        "selected_date": selected_date,
        "previous_day": selected_date - timedelta(days=1),
        "next_day": selected_date + timedelta(days=1),
        "timezone": timezone,
    }

    return render(request, "myapp/index.html", context)


def weekly_report(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    consumed = Consume.objects.filter(
        user=request.user, date__range=[start_date, end_date]
    ).order_by("date")

    total_calories = sum(item.total_calories for item in consumed)
    total_carbs = sum(item.total_carbs for item in consumed)
    total_proteins = sum(item.total_proteins for item in consumed)
    total_fats = sum(item.total_fats for item in consumed)

    context = {
        "weekly_data": consumed,
        "total_weekly_calories": total_calories,
        "total_weekly_carbs": total_carbs,
        "total_weekly_proteins": total_proteins,
        "total_weekly_fats": total_fats,
        "total_meals": consumed.count(),
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "myapp/weekly_report.html", context)


def monthly_report(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    consumed = Consume.objects.filter(
        user=request.user, date__range=[start_date, end_date]
    ).order_by("date")

    total_calories = sum(item.total_calories for item in consumed)
    total_carbs = sum(item.total_carbs for item in consumed)
    total_proteins = sum(item.total_proteins for item in consumed)
    total_fats = sum(item.total_fats for item in consumed)

    context = {
        "monthly_data": consumed,
        "total_monthly_calories": total_calories,
        "total_monthly_carbs": total_carbs,
        "total_monthly_proteins": total_proteins,
        "total_monthly_fats": total_fats,
        "total_meals": consumed.count(),
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "myapp/monthly_report.html", context)


def delete_consume(request, id):
    consumed_food = Consume.objects.get(id=id)
    if request.method == "POST":
        consumed_food.delete()
        return redirect(request.META.get("HTTP_REFERER", "index"))
    return render(request, "myapp/delete.html")


def home(request):
    return render(request, "myapp/home.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, "myapp/register.html", {"form": form})


@require_POST
def add_custom_food(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)

    try:
        # Calculate calories if not provided
        calories = request.POST.get("calories")
        if not calories:
            carbs = float(request.POST.get("carbs"))
            protein = float(request.POST.get("proteins"))
            fats = float(request.POST.get("fats"))
            calories = carbs * 4 + protein * 4 + fats * 9

        food = Food.objects.create(
            name=request.POST.get("food_name"),
            carbs_per_100g=float(request.POST.get("carbs")),
            proteins_per_100g=float(request.POST.get("proteins")),
            fats_per_100g=float(request.POST.get("fats")),
            calories_per_100g=float(calories),
            diet_type=request.POST.get("diet_type"),
            meal_time=request.POST.get("meal_time"),
            food_group=request.POST.get("food_group"),
            quantity=100,
        )
        return JsonResponse(
            {
                "id": food.id,
                "name": food.name,
                "calories": food.calories_per_100g,
                "carbs": food.carbs_per_100g,
                "proteins": food.proteins_per_100g,
                "fats": food.fats_per_100g,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
