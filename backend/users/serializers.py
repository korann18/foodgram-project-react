from users.models import User
from djoser.serializers import UserSerializer, UserCreateSerializer


class ProfileCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')


class ProfileSerializers(UserSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name'
        )
