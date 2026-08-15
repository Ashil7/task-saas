from rest_framework.permissions import BasePermission
from .models import Membership


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return Membership.objects.filter(
            user=request.user,
            role='ADMIN'
        ).exists()


    
    
class TaskPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        membership= Membership.objects.filter(
            user=request.user,
            organization=obj.project.organization
        ).first()
        
        if not membership:
            return False
        
        if membership.role in ['ADMIN','MANAGER']:
            return True
        
        if request.method in ['GET','HEAD','OPTIONS']:
            return True
        
        if request.method =='DELETE':
            return False
        
        if request.method in ['PUT','PATCH']:
            return obj.assigned_to.filter(
                id=request.user.id
            ).exists()
        
        return False