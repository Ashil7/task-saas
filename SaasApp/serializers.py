from rest_framework import serializers
from .models import Projects, Task

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'
        read_only_fields = ['organization']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields= ['created_by']
        
    def validate_assigned_to(self,users):
        request=self.context['request']
        task=self.instance
        
        if not task:
            return users
        
        organization=task.project.organization
        
        for user in users:
            if not user.memberships.filter(
                organization=organization
            ).exists():
                raise serializers.ValidationError(
                    f"{user.email} does not belong to this organization."
                )
        return users
