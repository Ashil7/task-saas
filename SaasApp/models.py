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
        ("MANAGER",'member'),
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