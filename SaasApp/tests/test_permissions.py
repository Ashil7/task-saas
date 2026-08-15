from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from SaasApp.models import User, Organization, Membership, Task, Projects

class AuthenticationTests(APITestCase):

    def test_unauthenticated_user_cannot_access_projects(self):
        response = self.client.get("/api/projects/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class ProjectPermissionTests(APITestCase):

    def setUp(self):
        
        self.org = Organization.objects.create(
            name="TechCorp"
        )

        
        self.admin = User.objects.create_user(
            email="admin@test.com",
            username="admin",
            password="Admin@123"
        )

        self.manager = User.objects.create_user(
            email="manager@test.com",
            username="manager",
            password="Manager@123"
        )

        self.member = User.objects.create_user(
            email="member@test.com",
            username="member",
            password="Member@123"
        )

        
        Membership.objects.create(
            user=self.admin,
            organization=self.org,
            role="ADMIN"
        )

        Membership.objects.create(
            user=self.manager,
            organization=self.org,
            role="MANAGER"
        )

        Membership.objects.create(
            user=self.member,
            organization=self.org,
            role="MEMBER"
        )

    def test_admin_can_create_project(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/projects/",
            {
                "name": "Admin Project",
                "description": "Created by admin"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_manager_cannot_create_project(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/projects/",
            {
                "name": "Manager Project",
                "description": "Should fail"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_member_cannot_create_project(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            "/api/projects/",
            {
                "name": "Member Project",
                "description": "Should fail"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        
        
class OrganizationIsolationTests(APITestCase):

    def setUp(self):
        # Organizations
        self.techcorp = Organization.objects.create(
            name="TechCorp"
        )

        self.othercorp = Organization.objects.create(
            name="OtherCorp"
        )

        # Users
        self.tech_admin = User.objects.create_user(
            email="techadmin@test.com",
            username="techadmin",
            password="Admin@123"
        )

        self.other_admin = User.objects.create_user(
            email="otheradmin@test.com",
            username="otheradmin",
            password="Admin@123"
        )

        # Memberships
        Membership.objects.create(
            user=self.tech_admin,
            organization=self.techcorp,
            role="ADMIN"
        )

        Membership.objects.create(
            user=self.other_admin,
            organization=self.othercorp,
            role="ADMIN"
        )

    def test_user_only_sees_own_organization_projects(self):
        # Create projects directly in the database
        from SaasApp.models import Projects

        tech_project = Projects.objects.create(
            name="TechCorp Project",
            description="TechCorp project",
            organization=self.techcorp
        )

        Projects.objects.create(
            name="OtherCorp Project",
            description="OtherCorp project",
            organization=self.othercorp
        )

        # Login as TechCorp admin
        self.client.force_authenticate(user=self.tech_admin)

        response = self.client.get("/api/projects/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Should only return TechCorp project
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]["id"],
            tech_project.id
        )

    def test_other_organization_project_is_not_visible(self):
        from SaasApp.models import Projects

        other_project = Projects.objects.create(
            name="OtherCorp Secret Project",
            description="Private project",
            organization=self.othercorp
        )

        self.client.force_authenticate(user=self.tech_admin)

        response = self.client.get("/api/projects/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        project_ids = [
            project["id"]
            for project in response.data
        ]

        self.assertNotIn(
            other_project.id,
            project_ids
        )


class TaskOrganizationIsolationTests(APITestCase):

    def setUp(self):
        self.techcorp = Organization.objects.create(
            name="TechCorp"
        )

        self.othercorp = Organization.objects.create(
            name="OtherCorp"
        )

        self.tech_user = User.objects.create_user(
            email="techuser@test.com",
            username="techuser",
            password="Test@123"
        )

        Membership.objects.create(
            user=self.tech_user,
            organization=self.techcorp,
            role="MEMBER"
        )

        self.other_project = Projects.objects.create(
            name="OtherCorp Project",
            description="Private project",
            organization=self.othercorp
        )

    def test_cannot_create_task_in_other_organization(self):

        self.client.force_authenticate(
            user=self.tech_user
        )

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Cross Org Task",
                "description": "Should not be created",
                "status": "NEW",
                "priority": "HIGH",
                "project": self.other_project.id,
                "assigned_to": []
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            Task.objects.count(),
            0
        )
        
class TaskPermissionTests(APITestCase):

    def setUp(self):
        self.org = Organization.objects.create(
            name="TechCorp"
        )

        self.admin = User.objects.create_user(
            email="admin@test.com",
            username="admin",
            password="Admin@123"
        )

        self.manager = User.objects.create_user(
            email="manager@test.com",
            username="manager",
            password="Manager@123"
        )

        self.member = User.objects.create_user(
            email="member@test.com",
            username="member",
            password="Member@123"
        )

        Membership.objects.create(
            user=self.admin,
            organization=self.org,
            role="ADMIN"
        )

        Membership.objects.create(
            user=self.manager,
            organization=self.org,
            role="MANAGER"
        )

        Membership.objects.create(
            user=self.member,
            organization=self.org,
            role="MEMBER"
        )

        self.project = Projects.objects.create(
            name="TechCorp Project",
            description="Test project",
            organization=self.org
        )

    def create_task(self):
        return Task.objects.create(
            title="Test Task",
            description="Testing permissions",
            status="NEW",
            priority="HIGH",
            project=self.project,
            created_by=self.admin
        )

    def test_admin_can_create_task(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Admin Task",
                "description": "Created by admin",
                "status": "NEW",
                "priority": "HIGH",
                "project": self.project.id,
                "assigned_to": []
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_manager_can_create_task(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Manager Task",
                "description": "Created by manager",
                "status": "NEW",
                "priority": "MEDIUM",
                "project": self.project.id,
                "assigned_to": []
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_member_can_create_task(self):
        self.client.force_authenticate(user=self.member)

        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Member Task",
                "description": "Created by member",
                "status": "NEW",
                "priority": "LOW",
                "project": self.project.id,
                "assigned_to": []
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_member_cannot_assign_user(self):
        task = self.create_task()

        self.client.force_authenticate(user=self.member)

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {
                "assigned_to": [self.member.id]
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        
    def test_project_cannot_be_changed(self):
        task = self.create_task()

        another_project = Projects.objects.create(
            name="Another Project",
            description="Another TechCorp project",
            organization=self.org
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {
                "project": another_project.id
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        
    

    def test_cannot_assign_user_from_another_organization(self):
        other_org = Organization.objects.create(
            name="OtherCorp"
        )

        other_user = User.objects.create_user(
            email="otheruser@test.com",
            username="otheruser",
            password="Other@123"
        )

        Membership.objects.create(
            user=other_user,
            organization=other_org,
            role="MEMBER"
        )

        task = self.create_task()

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {
                "assigned_to": [other_user.id]
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    
    def test_assigned_member_can_update_task(self):
        task = self.create_task()

        task.assigned_to.add(self.member)

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {
                "title": "Updated by assigned member"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unassigned_member_cannot_update_task(self):
        task = self.create_task()

        self.client.force_authenticate(
            user=self.member
        )

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {
                "title": "Should not be allowed"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )