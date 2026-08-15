from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .models import Projects, Task, Membership
from .serializers import ProjectSerializer,TaskSerializer
from .permissions import IsAdmin, TaskPermission



class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class=ProjectSerializer
    permission_classes=[IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create','destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        return Projects.objects.filter(
            organization__memberships__user=self.request.user
        ).select_related("organization")
    
    def perform_create(self, serializer):
        membership=Membership.objects.filter(user=self.request.user).first()
        
        
        if not membership:
            raise PermissionDenied(
                "You are not a member of any organization."
            )
        serializer.save(organization=membership.organization)
        
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class=TaskSerializer
    permission_classes=[TaskPermission]
    
    
    def get_queryset(self):
        return (
            Task.objects
            .filter(project__organization__memberships__user=self.request.user)
            .select_related("project", "created_by")
            .prefetch_related("assigned_to")
        )
    
    def perform_create(self, serializer):
        membership = Membership.objects.filter(user=self.request.user).first()
        if not membership:
            raise PermissionDenied(
                 "You are not a member of any organization."
             )
        project = serializer.validated_data["project"]

        if project.organization != membership.organization:
            raise PermissionDenied("You cannot create tasks in another organization.")

        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        if 'project' in self.request.data:
            raise PermissionDenied(
                "Project cannot be changed after task creation."
            )
            
        if 'assigned_to' in self.request.data:
            membership = Membership.objects.filter(
                user=self.request.user
            ).first()
            
            if not membership:
                raise PermissionDenied(
                    "You are not a member of any organization."
                )
            if membership.role not in ['ADMIN', 'MANAGER']:
                        raise PermissionDenied(
                            "Only admins and managers can assign users to tasks."
                        )

            
        serializer.save()