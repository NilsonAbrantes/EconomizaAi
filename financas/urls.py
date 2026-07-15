from django.urls import path

from . import views

app_name = "financas"

urlpatterns = [
    path("", views.novo_registro, name="novo"),
    path("historico/", views.historico, name="historico"),
    path("registro/<int:pk>/", views.detalhes_registro, name="detalhes"),
    path("registro/<int:pk>/editar/", views.editar_registro, name="editar"),
    path("registro/<int:pk>/excluir/", views.excluir_registro, name="excluir"),
    path("exportar-csv/", views.exportar_csv, name="exportar_csv"),
]
