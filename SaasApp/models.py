from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email=models.EmailField(unique=True)
    
    
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    
    def __str__(self):
        return self.email   
    
class Organization(models.Model):
    name=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    ROLE_CHOICES=(
        ("ADMIN",'admin'),
        ("MANAGER",'manager'),
        ("MEMBER","member"),
    )
    
    user =models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    
    organization=models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    
    role= models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="MEMBER"
    )
    
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=("user","organization")
        
    def __str__(self):
        return f"{self.user.email}-{self.organization.name}({self.role})"
    
    
class Projects(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
        
    organization=models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects'
    )
        
    created_at=models.DateTimeField(auto_now_add=True)
        
        
    def __str__(self):
        return f"{self.name}({self.organization.name})"
    
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        
class Task(models.Model):
        STATUS_CHOICES=[
            ("NEW","new"),
            ("IN_PROGRESS", 'in progress'),
            ("DONE",'done'),
        ]
            
        PRIORITY_CHOICES=[
            ("LOW",'low'),
            ('MEDIUM','medium'),
            ('HIGH','high'),
        ]
            
        title=models.CharField(max_length=255)
        description=models.TextField(blank=True,null=True)
            
            
        project=models.ForeignKey(
            Projects,
            on_delete=models.CASCADE,
            related_name='tasks'
        )
        
        
        assigned_to=models.ManyToManyField(
            User,
            related_name='assigned_tasks',
            blank=True
        )
        
        status=models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default='NEW',
        )
        
        priority=models.CharField(
            max_length=20,
            choices=PRIORITY_CHOICES,
            default='MEDIUM',
        )
        
        created_by = models.ForeignKey(User, on_delete=models.CASCADE)        
        due_date=models.DateField(blank=True,null=True)
        
        created_at=models.DateTimeField(auto_now_add=True)
        
        
        
        class Meta:
            indexes = [
                models.Index(fields=["project", "status"]),
                models.Index(fields=["created_by"]),
                models.Index(fields=["due_date"]),
            ]
        
        def __str__(self):
            return f"{self.title}({self.project.name})"
        
        