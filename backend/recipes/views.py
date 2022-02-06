from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from reportlab.pdfgen.canvas import Canvas

from recipes.pagination import CustomPaginator
from recipes.permissions import IsAuthorOrReadOnly
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                 RecipeListSerializer, RecipeSerializer,
                                 ShoppingCartSerializer, TagSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['POST'])
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavoriteSerializer(data=data,
                                        context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite, user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=[IsAuthenticated],
            methods=['POST'])
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingCartSerializer(data=data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart, user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def canvas_method(dictionary):
        begin_position_x, begin_position_y = 30, 730
        response = HttpResponse(
            content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"')
        canvas = Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans', '../../data/FreeSans.ttf'))
        canvas.setFont('FreeSans', 25)
        canvas.setTitle('СПИСОК ПОКУПОК')
        canvas.drawString(begin_position_x,
                          begin_position_y + 40, 'Список покупок: ')
        canvas.setFont('FreeSans', 18)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 730
                canvas.showPage()
                canvas.setFont('FreeSans', 18)
            canvas.drawString(
                begin_position_x,
                begin_position_y,
                f'Позиция №{number}: {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}'
            )
            begin_position_y -= 30
        canvas.showPage()
        canvas.save()
        return response

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_carts__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(ingredient_total=Sum('amount'))
        return RecipeViewSet.canvas_method(ingredients)
