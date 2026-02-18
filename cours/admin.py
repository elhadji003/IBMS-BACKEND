from django.contrib import admin
from .models import Course, CoursePayment, CourseContent

# 1. Gestion des contenus (Vidéos/Fichiers) à l'intérieur de la page du Cours
class CourseContentInline(admin.TabularInline):
    model = CourseContent
    extra = 1 # Permet d'ajouter un contenu directement depuis la page du cours

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_active', 'partner') # On affiche le partenaire
    list_filter = ('is_active', 'partner') # Filtrer par partenaire ou statut
    search_fields = ('title',)
    inlines = [CourseContentInline] # Affiche les vidéos directement sous le cours

@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    # Très important pour suivre l'argent
    list_display = ('id', 'user', 'course', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'course')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('created_at',) # On ne peut pas modifier la date
    
    # Coloration des statuts pour y voir clair
    list_editable = ('status',) # Permet de changer le statut rapidement sans ouvrir la page

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)