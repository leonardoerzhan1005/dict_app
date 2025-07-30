from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Word, Language, Category, CategoryTranslation, Tag, TagTranslation

def get_translation(language_code, key, default=None):
    """
    Простая функция для получения переводов (заглушка)
    """
    return default or key

def home(request):
    """
    Главная страница с поиском слов
    """
    # Получить параметры поиска
    query = request.GET.get('q', '').strip()
    language_code = request.GET.get('lang', '')
    category_id = request.GET.get('category', '')
    letter = request.GET.get('letter', '')
    page = request.GET.get('page', 1)
    
    # Базовый queryset - только одобренные и не удалённые слова
    words = Word.objects.filter(status='approved', is_deleted=False)
    
    # Фильтр по языку
    if language_code:
        words = words.filter(language__code=language_code)
    
    # Фильтр по категории
    if category_id:
        words = words.filter(category_id=category_id)
    
    # Фильтр по первой букве
    if letter:
        words = words.filter(word__istartswith=letter)
    
    # Поиск по запросу
    if query:
        # Автоматическое определение языка запроса
        detected_language = detect_language(query)
        
        # Поиск по слову и значению на всех языках
        search_query = Q(word__icontains=query) | Q(meaning__icontains=query)
        
        # Если определили язык, приоритет поиску на этом языке
        if detected_language:
            words = words.filter(
                Q(language__code=detected_language) & search_query
            ) | words.filter(
                ~Q(language__code=detected_language) & search_query
            )
        else:
            words = words.filter(search_query)
    
    # Сортировка
    words = words.order_by('word')
    
    # Пагинация
    paginator = Paginator(words, 20)  # 20 слов на страницу
    words_page = paginator.get_page(page)
    
    # Получить данные для фильтров
    languages = Language.objects.all()
    categories = Category.objects.all()
    alphabet = get_alphabet()
    
    # Получить переводы названий категорий
    user_language = request.session.get('language', 'ru')
    categories_with_translations = []
    for category in categories:
        try:
            translation = CategoryTranslation.objects.get(
                category=category, 
                language__code=user_language
            )
            categories_with_translations.append({
                'category': category,
                'name': translation.name
            })
        except CategoryTranslation.DoesNotExist:
            categories_with_translations.append({
                'category': category,
                'name': category.code
            })
    
    context = {
        'words': words_page,
        'languages': languages,
        'categories': categories_with_translations,
        'alphabet': alphabet,
        'current_query': query,
        'current_language': language_code,
        'current_category': category_id,
        'current_letter': letter,
        'user_language': user_language,
    }
    
    return render(request, 'dictionary/home.html', context)

def word_detail(request, word_id):
    """
    Детальная страница слова с переводами
    """
    word = get_object_or_404(Word, id=word_id, status='approved', is_deleted=False)
    
    # Получить все переводы слова
    translations = word.from_translations.all().select_related('to_word', 'to_word__language')
    
    # Получить примеры
    examples = word.examples.all()
    
    # Получить теги с переводами
    user_language = request.session.get('language', 'ru')
    tags_with_translations = []
    for tag in word.tags.all():
        try:
            translation = TagTranslation.objects.get(
                tag=tag, 
                language__code=user_language
            )
            tags_with_translations.append({
                'tag': tag,
                'name': translation.name
            })
        except TagTranslation.DoesNotExist:
            tags_with_translations.append({
                'tag': tag,
                'name': tag.code
            })
    
    context = {
        'word': word,
        'translations': translations,
        'examples': examples,
        'tags': tags_with_translations,
        'user_language': user_language,
    }
    
    return render(request, 'dictionary/word_detail.html', context)

@require_http_methods(["GET"])
def search_ajax(request):
    """
    AJAX поиск для автодополнения
    """
    query = request.GET.get('q', '').strip()
    language_code = request.GET.get('lang', '')
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    # Поиск слов
    words = Word.objects.filter(
        status='approved', 
        is_deleted=False,
        word__icontains=query
    )
    
    if language_code:
        words = words.filter(language__code=language_code)
    
    # Ограничить результаты
    words = words[:10]
    
    results = []
    for word in words:
        results.append({
            'id': word.id,
            'word': word.word,
            'meaning': word.meaning[:100] + '...' if len(word.meaning) > 100 else word.meaning,
            'language': word.language.code,
            'url': f'/word/{word.id}/'
        })
    
    return JsonResponse({'results': results})

def detect_language(text):
    """
    Простое определение языка по символам
    """
    if not text:
        return None
    
    # Простые правила определения языка
    kazakh_chars = set('әғқңөұүіһ')
    russian_chars = set('ёйцукенгшщзхъфывапролджэячсмитьбю')
    turkish_chars = set('çğıöşü')
    
    text_lower = text.lower()
    
    # Подсчитать символы
    kazakh_count = sum(1 for char in text_lower if char in kazakh_chars)
    russian_count = sum(1 for char in text_lower if char in russian_chars)
    turkish_count = sum(1 for char in text_lower if char in turkish_chars)
    
    # Определить язык по наибольшему количеству символов
    if kazakh_count > 0:
        return 'kk'
    elif russian_count > 0:
        return 'ru'
    elif turkish_count > 0:
        return 'tr'
    else:
        return 'en'  # По умолчанию английский

def get_alphabet():
    """
    Получить алфавит для фильтрации
    """
    # Можно расширить для разных языков
    return [chr(i) for i in range(ord('А'), ord('Я')+1)] + [chr(i) for i in range(ord('A'), ord('Z')+1)]

@login_required
def add_to_favorites(request, word_id):
    """
    Добавить слово в избранное
    """
    if request.method == 'POST':
        word = get_object_or_404(Word, id=word_id)
        from .models import Favourite
        
        favourite, created = Favourite.objects.get_or_create(
            user=request.user,
            word=word
        )
        
        if created:
            return JsonResponse({'status': 'added'})
        else:
            favourite.delete()
            return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'error'})
