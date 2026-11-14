from django.contrib.auth.models import User
from django.test import TestCase

from .models import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, Branch, UserProfile
from .services import get_access, get_role, get_user_branch


class RoleAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.get(code="TLT")
        cls.branch2 = Branch.objects.get(code="SZR")

    def _user(self, role, branch=None, is_superuser=False):
        user = User.objects.create_user("u_" + role + str(branch.pk if branch else "x"), is_superuser=is_superuser)
        if role and not is_superuser:
            UserProfile.objects.create(user=user, role=role, branch=branch)
        return user

    def test_superuser_is_admin(self):
        user = self._user(ROLE_ADMIN, is_superuser=True)
        self.assertEqual(get_role(user), ROLE_ADMIN)
        self.assertTrue(get_access(user)[0])

    def test_operator_branch(self):
        user = self._user(ROLE_OPERATOR, branch=self.branch)
        allowed, branch = get_access(user)
        self.assertTrue(allowed)
        self.assertEqual(branch, self.branch)
        self.assertEqual(get_user_branch(user), self.branch)

    def test_manager_global(self):
        user = self._user(ROLE_MANAGER)
        allowed, branch = get_access(user)
        self.assertTrue(allowed)
        self.assertIsNone(branch)

    def test_user_without_profile_no_access(self):
        user = User.objects.create_user("no_profile")
        self.assertFalse(get_access(user)[0])
        self.assertIsNone(get_role(user))