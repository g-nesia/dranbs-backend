from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from backend.models import Ticket, UserProfile, Product, Board, BoardProduct, BoardFollower


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.IntegerField()
    birthday = serializers.DateField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    password_confirm = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField()

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        password = validated_data.get('password', None)
        if password:
            instance.set_password(validated_data['password'])
        instance.save()
        instance.profile.gender = validated_data['gender']
        instance.profile.birthday = validated_data.get('birthday', None)
        instance.profile.country = validated_data['country']
        instance.profile.save()
        return instance

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        UserProfile.objects.create(
            user=user,
            gender=validated_data['gender'],
            country=validated_data['country'],
            birthday=validated_data.get('birthday', None)
        )
        return user

    def validate_username(self, username):
        if self.instance and self.instance.username == username:
            return username
        else:
            try:
                User.objects.get(username=username)
                raise serializers.ValidationError("username already taken")
            except User.DoesNotExist:
                return username

    def validate_email(self, email):
        if self.instance and self.instance.email == email:
            return email
        else:
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
        if not self.instance:
            if data['password_confirm'] != data['password']:
                raise serializers.ValidationError({
                    "password_confirm": "password doesn't match"
                })
        else:
            password = data.get('password', None)
            password_confirm = data.get('password_confirm', None)
            if password:
                if password_confirm != password:
                    raise serializers.ValidationError({
                        "password_confirm": "password doesn't match"
                    })
        return data


class CreateBoardSerializer(serializers.Serializer):
    board_name = serializers.CharField()
    board_type = serializers.ChoiceField(choices=[0, 1])
    product_id = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_board_name(self, board_name):
        user = self.user
        try:
            Board.objects.get(name=board_name, user_id=user.id)
            raise serializers.ValidationError("This name already exists in your boards.")
        except Board.DoesNotExist:
            return board_name

    def validate_product_id(self, value):
        try:
            Product.objects.get(pk=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("product doesn't exists.")


class FollowBoardSerializer(serializers.Serializer):
    slug = serializers.CharField()
    username = serializers.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        board = Board.objects.get(slug=validated_data['slug'], user__username=validated_data['username'])
        try:
            board_follower = BoardFollower.objects.get(board_id=board.id, user_id=self.user.id)
            board_follower.delete()
            followers = BoardFollower.objects.filter(board_id=board.id).count()
            result = {
                'followers': followers,
                'is_following': False
            }
            return result
        except BoardFollower.DoesNotExist:
            BoardFollower.objects.create(board_id=board.id, user_id=self.user.id)
            followers = BoardFollower.objects.filter(board_id=board.id).count()
            result = {
                'followers': followers,
                'is_following': True
            }
            return result

    def validate_username(self, username):
        try:
            User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            raise serializers.ValidationError("user doesn't exists.")

    def validate(self, data):
        try:
            Board.objects.get(slug=data['slug'], user__username=data['username'])
            return data
        except Board.DoesNotExist:
            raise serializers.ValidationError("board doesn't exists.")


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class BoardProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardProduct
        fields = ['product', 'board']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
