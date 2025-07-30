from django.urls import path
from . import views

app_name = 'dictionary'

urlpatterns = [
    # Главная страница с поиском
    path('', views.home, name='home'),
    
    # Детальная страница слова
    path('word/<int:word_id>/', views.word_detail, name='word_detail'),
    
    # AJAX поиск для автодополнения
    path('search/ajax/', views.search_ajax, name='search_ajax'),
    
    # Добавление в избранное
    path('favorites/add/<int:word_id>/', views.add_to_favorites, name='add_to_favorites'),
] 