from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Food(models.Model):
    # Diet Types
    VEG = "VEG"
    NON_VEG = "NON_VEG"
    DIET_TYPE_CHOICES = [
        (VEG, "Vegetarian"),
        (NON_VEG, "Non-Vegetarian"),
    ]

    # Meal Times
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACK = "SNACK"
    MEAL_TIME_CHOICES = [
        (BREAKFAST, "Breakfast"),
        (LUNCH, "Lunch"),
        (DINNER, "Dinner"),
        (SNACK, "Snack"),
    ]

    # Food Groups
    BREAD = "BREAD"
    VEGETABLE = "VEGETABLE"
    RICE = "RICE"
    DRYFRUIT = "DRYFRUIT"
    DAIRY = "DAIRY"
    ANIMAL = "ANIMAL"
    FRUIT = "FRUIT"
    BEVERAGE = "BEVERAGE"
    LENTILS = "LENTILS"
    LEGUMES = "LEGUMES"
    FOOD_GROUP_CHOICES = [
        (BREAD, "Bread"),
        (VEGETABLE, "Vegetable"),
        (RICE, "Rice"),
        (DRYFRUIT, "Dry Fruit"),
        (DAIRY, "Dairy Product"),
        (ANIMAL, "Animal Product"),
        (FRUIT, "Fruit"),
        (BEVERAGE, "Beverage"),
        (LENTILS, "Lentils"),
        (LEGUMES, "Legumes"),
    ]

    name = models.CharField(max_length=100)
    carbs_per_100g = models.FloatField(default=0)  # Carbs per 100g
    proteins_per_100g = models.FloatField(default=0)  # Proteins per 100g
    fats_per_100g = models.FloatField(default=0)  # Fats per 100g
    calories_per_100g = models.IntegerField(default=0)  # Calories per 100g
    quantity = models.FloatField(default=100)  # Quantity in grams (default: 100g)
    diet_type = models.CharField(max_length=10, choices=DIET_TYPE_CHOICES, default=VEG)
    meal_time = models.CharField(
        max_length=10, choices=MEAL_TIME_CHOICES, default=LUNCH
    )
    food_group = models.CharField(
        max_length=10, choices=FOOD_GROUP_CHOICES, default=VEGETABLE
    )

    def __str__(self):
        return self.name

    # Dynamic properties that scale with quantity
    @property
    def carbs(self):
        return (self.carbs_per_100g / 100) * self.quantity

    @property
    def proteins(self):
        return (self.proteins_per_100g / 100) * self.quantity

    @property
    def fats(self):
        return (self.fats_per_100g / 100) * self.quantity

    @property
    def calories(self):
        return (self.calories_per_100g / 100) * self.quantity

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]


class Consume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_consumed = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_consumed = models.FloatField(default=100)  # Quantity consumed in grams
    date = models.DateField(default=timezone.now)

    # Calculate macros for the consumed quantity
    @property
    def total_calories(self):
        return (self.food_consumed.calories_per_100g / 100) * self.quantity_consumed

    @property
    def total_proteins(self):
        return (self.food_consumed.proteins_per_100g / 100) * self.quantity_consumed

    @property
    def total_carbs(self):
        return (self.food_consumed.carbs_per_100g / 100) * self.quantity_consumed

    @property
    def total_fats(self):
        return (self.food_consumed.fats_per_100g / 100) * self.quantity_consumed

    def __str__(self):
        return f"{self.user.username} consumed {self.food_consumed.name} ({self.quantity_consumed}g)"


class CalorieGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calorie_goal = models.IntegerField(default=2000)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ("user", "date")  # One goal per user per day

    def __str__(self):
        return f"{self.user.username}'s Calorie Goal for {self.date}"
