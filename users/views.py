from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, PasswordChangeSerializer


# ============ Web Views ============

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login view with first login check
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Check if first login
            if user.first_login:
                messages.warning(request, 'You must change your temporary password.')
                return redirect('change_password')

            return redirect('query_create')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """
    View for changing password on first login
    """
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'users/change_password.html')

        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'users/change_password.html')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'users/change_password.html')

        request.user.set_password(new_password)
        request.user.first_login = False
        request.user.save()

        messages.success(request, 'Password changed successfully.')
        return redirect('login')

    return render(request, 'users/change_password.html')


def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# ============ API Views ============

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for User model (read-only for regular users)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(project=user.project)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user info
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change password endpoint
        """
        serializer = PasswordChangeSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(serializer.validated_data['new_password'])
            user.first_login = False
            user.save()

            return Response({'message': 'Password changed successfully'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    API Login endpoint that returns JWT tokens
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'first_login': user.first_login
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )