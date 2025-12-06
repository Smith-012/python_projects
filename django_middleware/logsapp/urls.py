from django.urls import path
from .views import logs_graph

urlpatterns = [
    path("logs-graph/", logs_graph, name="logs_graph"),
]
