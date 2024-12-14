from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Restrict queryset to only objects owned by the authenticated user
        return Todo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the authenticated user with the Todo
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)


from django.shortcuts import render


def todo_app_view(request):
    return render(request, "todo_app.html")
