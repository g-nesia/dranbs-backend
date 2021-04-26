from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

from authemail.utils import make_username


class SignupSerializer(serializers.Serializer):
    """
    Don't require email to be unique so visitor can signup multiple times,
    if misplace verification email.  Handle in view.
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=30, default='',
                                       required=False)
    last_name = serializers.CharField(max_length=30, default='',
                                      required=False)
    gender = serializers.IntegerField()
    birthday = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    password_confirm = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    def validate_email(self, email):
        User = get_user_model()
        try:
            User.objects.get(email=email)
            raise serializers.ValidationError("email already taken")
        except User.DoesNotExist:
            return email

    def validate_password(self, password):
        if self.instance:
            if password:
                password_validation.validate_password(password)
        else:
            password_validation.validate_password(password)
        return password

    def validate(self, data):
        if data['password_confirm'] != data['password']:
            raise serializers.ValidationError({
                "password_confirm": "password doesn't match"
            })
        return data

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        User = get_user_model()
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        username = make_username(first_name, last_name)
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordResetVerifiedSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=40)
    password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmailChangeVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'username', 'gender', 'birthday', 'is_verified',)
