from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Language, CustomUser, Category, CategoryTranslation, Tag, TagTranslation,
    Word, Translation, Example, Favourite, SearchHistory, WordLike,
    WordChangeLog, WordHistory, InterfaceTranslation
)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']

class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'get_translations']
    search_fields = ['code']
    inlines = [CategoryTranslationInline]
    
    def get_translations(self, obj):
        translations = obj.translations.all()[:3]
        return ', '.join([f"{t.language.code}: {t.name}" for t in translations])
    get_translations.short_description = 'Переводы'

class TagTranslationInline(admin.TabularInline):
    model = TagTranslation
    extra = 1

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['code', 'get_translations']
    search_fields = ['code']
    inlines = [TagTranslationInline]
    
    def get_translations(self, obj):
        translations = obj.translations.all()[:3]
        return ', '.join([f"{t.language.code}: {t.name}" for t in translations])
    get_translations.short_description = 'Переводы'

class TranslationInline(admin.TabularInline):
    model = Translation
    fk_name = 'from_word'
    extra = 1
    verbose_name = 'Перевод'
    verbose_name_plural = 'Переводы'

class ExampleInline(admin.TabularInline):
    model = Example
    extra = 1

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'language', 'category', 'status', 'difficulty', 'is_deleted', 'created_by', 'created_at']
    list_filter = ['language', 'status', 'difficulty', 'is_deleted', 'created_at', 'category']
    search_fields = ['word', 'meaning', 'pronunciation']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TranslationInline, ExampleInline]
    actions = ['approve_words', 'reject_words', 'mark_as_deleted', 'restore_words']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('word', 'language', 'meaning', 'pronunciation', 'difficulty')
        }),
        ('Классификация', {
            'fields': ('category', 'tags', 'status')
        }),
        ('Медиа', {
            'fields': ('image', 'audio', 'example_audio', 'file'),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('is_deleted', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_words(self, request, queryset):
        queryset.update(status='approved')
    approve_words.short_description = 'Одобрить выбранные слова'
    
    def reject_words(self, request, queryset):
        queryset.update(status='rejected')
    reject_words.short_description = 'Отклонить выбранные слова'
    
    def mark_as_deleted(self, request, queryset):
        queryset.update(is_deleted=True)
    mark_as_deleted.short_description = 'Пометить как удалённые'
    
    def restore_words(self, request, queryset):
        queryset.update(is_deleted=False)
    restore_words.short_description = 'Восстановить слова'

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['from_word', 'to_word', 'status', 'order', 'note']
    list_filter = ['status', 'from_word__language', 'to_word__language']
    search_fields = ['from_word__word', 'to_word__word', 'note']
    ordering = ['from_word', 'order']

@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ['word', 'text_preview', 'author', 'created_at']
    list_filter = ['created_at', 'word__language']
    search_fields = ['text', 'word__word']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'added_at']
    list_filter = ['added_at', 'word__language']
    search_fields = ['user__username', 'word__word']
    readonly_fields = ['added_at']

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'searched_at']
    list_filter = ['searched_at']
    search_fields = ['user__username', 'word']
    readonly_fields = ['searched_at']
    ordering = ['-searched_at']

@admin.register(WordLike)
class WordLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'is_like', 'created_at']
    list_filter = ['is_like', 'created_at', 'word__language']
    search_fields = ['user__username', 'word__word']
    readonly_fields = ['created_at']

@admin.register(WordChangeLog)
class WordChangeLogAdmin(admin.ModelAdmin):
    list_display = ['word', 'user', 'action', 'change_type', 'timestamp']
    list_filter = ['action', 'change_type', 'timestamp', 'word__language']
    search_fields = ['word__word', 'user__username', 'comment']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(WordHistory)
class WordHistoryAdmin(admin.ModelAdmin):
    list_display = ['word', 'changed_by', 'changed_at']
    list_filter = ['changed_at', 'word__language']
    search_fields = ['word__word', 'changed_by__username']
    readonly_fields = ['changed_at', 'data']
    ordering = ['-changed_at']

@admin.register(InterfaceTranslation)
class InterfaceTranslationAdmin(admin.ModelAdmin):
    list_display = ['language', 'key', 'value_preview']
    list_filter = ['language']
    search_fields = ['key', 'value']
    ordering = ['language', 'key']
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Значение'

# Расширенная админка для CustomUser
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'preferred_language', 'is_moderator', 'is_verified', 'is_staff', 'is_active']
    list_filter = ['is_moderator', 'is_verified', 'is_staff', 'is_active', 'preferred_language', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('preferred_language', 'bio', 'avatar', 'is_moderator', 'is_verified', 'registration_source')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('preferred_language', 'bio', 'avatar', 'is_moderator', 'is_verified', 'registration_source')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# Настройки админки
admin.site.site_header = 'Админка многоязычного словаря'
admin.site.site_title = 'Словарь'
admin.site.index_title = 'Управление словарём'
