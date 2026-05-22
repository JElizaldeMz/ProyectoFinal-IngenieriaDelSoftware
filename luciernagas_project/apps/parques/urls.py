from django.urls import path
from . import views

app_name = 'parques'

urlpatterns = [
    path('',            views.landing,          name='landing'),
    path('mapa/',       views.mapa,             name='mapa'),
    path('api/parques/', views.parques_json_api, name='api_parques'),
    path('<int:pk>/',   views.detalle_parque,   name='detalle'),

    path('admin/crear/',           views.ParqueCreateView.as_view(), name='crear'),
    path('admin/<int:pk>/editar/', views.ParqueUpdateView.as_view(), name='editar'),
    path('admin/<int:pk>/eliminar/', views.ParqueDeleteView.as_view(), name='eliminar'),
    path('admin/lista/',           views.ParqueListView.as_view(),   name='lista_admin'),
]
