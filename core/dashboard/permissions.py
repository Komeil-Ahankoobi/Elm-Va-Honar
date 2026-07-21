from django.contrib.auth.mixins import UserPassesTestMixin


class HasAdminAccessPermission(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return (self.request.user.is_staff == True) and (self.request.user.is_superuser == False)
        return False


class HasCustomerAccessPermission(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return (self.request.user.is_staff == False) and (self.request.user.is_superuser == False)
        return False



