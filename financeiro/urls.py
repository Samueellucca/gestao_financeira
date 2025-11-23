from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('registros/', views.RegistroListView.as_view(), name='registro_list'),
    path('registros/novo/', views.RegistroCreateView.as_view(), name='registro_novo'),
    path('registros/editar/<int:pk>/', views.RegistroUpdateView.as_view(), name='registro_editar'),
    path('registros/excluir/<int:pk>/', views.excluir_registro, name='registro_excluir'),
    
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_novo'),
    path('categorias/editar/<int:pk>/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/excluir/<int:pk>/', views.CategoriaDeleteView.as_view(), name='categoria_excluir'),

    # URL para exportar os registros para CSV
    path('registros/export/csv/', views.export_registros_csv, name='export_registros_csv'),

    # URL para processamento de voz
    path('processar-voz/', views.processar_voz, name='processar_voz'),
]