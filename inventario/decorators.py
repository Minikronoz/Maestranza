from django.contrib.auth.mixins import UserPassesTestMixin

class GroupRequiredMixin(UserPassesTestMixin):
    group_required = []  

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.groups.filter(name__in=self.group_required).exists() or user.is_superuser
        )
