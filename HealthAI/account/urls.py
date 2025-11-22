from django.urls import path
from .views import SignupAPI, LoginAPI, UserDashboard, UserListView, UserProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('signup/', SignupAPI.as_view(), name='api-signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/', UserDashboard.as_view(), name='user-dashboard'),
    path('admin/users/', UserListView.as_view(), name='admin-user-list'),
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
]
