import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            usuNom="testuser",
            usuContra="testpass123",
            usuEmail="test@example.com",
        )
        assert user.usuNom == "testuser"
        assert user.usuEmail == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active

    def test_create_user_without_username_raises(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                usuNom="",
                usuContra="testpass123",
                usuEmail="test@example.com",
            )

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError):
            User.objects.create_user(
                usuNom="testuser",
                usuContra="testpass123",
                usuEmail="",
            )

    def test_user_str(self):
        user = User.objects.create_user(
            usuNom="testuser",
            usuContra="testpass123",
            usuEmail="test@example.com",
        )
        assert str(user) == "testuser"
