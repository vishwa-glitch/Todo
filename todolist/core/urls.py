from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet, todo_app_view
from . import views

router = DefaultRouter()
router.register(r"todos", TodoViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("todo-app/", todo_app_view, name="todo_app"),
]
