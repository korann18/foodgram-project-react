from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Тег')
    color = models.CharField(
        max_length=7, unique=True, verbose_name='HEX-код')
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор рецепта', related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientAmount', verbose_name='Ингредиенты'
    )

    name = models.CharField(
        max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/', verbose_name='Картинка блюда')
    text = models.CharField(
        max_length=500, verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(
            1, message='Время приготовления - положительное число'
        )]
    )

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1, message='Количество ингредиентов - положительное число'
        )]
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
