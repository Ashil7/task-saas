from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .models import Projects, Task, Membership
from .serializers import ProjectSerializer,TaskSerializer
from .permissions import isAdmin



class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class=ProjectSerializer
    permission_classes=[IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create','destroy']:
            return [isAdmin()]
        return [IsAuthenticated]
    
    def get_queryset(self):
        membership=Membership.objects.get(user=self.request.user)
        return Projects.objects.filter(organization=membership.organization)
    
    def perform_create(self, serializer):
        membership=Membership.objects.get(user=self.request.user)
        serializer.save(organization=membership.organization)
        
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class=TaskSerializer
    permission_classes=[IsAuthenticated]
    
    
    def get_queryset(self):
        membership=Membership.objects.get(user=self.request.user)
        return Task.objects.get(project__organization=membership.organization)
    
    def perform_create(self, serializer):
        membership = Membership.objects.get(user=self.request.user)
        project = serializer.validated_data["project"]

        if project.organization != membership.organization:
            raise PermissionDenied("You cannot create tasks in another organization.")

        serializer.save()