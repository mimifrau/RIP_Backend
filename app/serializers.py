import os

from rest_framework import serializers

from .models import *


class CodesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, code):
        if code.image:
            return code.image.url.replace("minio", os.getenv("IP_ADDRESS"), 1)

        return f"http://{os.getenv("IP_ADDRESS")}:9000/images/default.png"

    class Meta:
        model = Code
        fields = ("id", "name", "status", "decryption", "image")


class CodeSerializer(CodesSerializer):
    class Meta:
        model = Code
        fields = "__all__"


class CodeAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ("name", "description", "decryption", "image")


class TaxsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tax
        fields = "__all__"


class TaxSerializer(TaxsSerializer):
    codes = serializers.SerializerMethodField()

    def get_codes(self, tax):
        items = tax.codetax_set.all()
        return [CodeItemSerializer(item.code, context={"paid": item.paid}).data for item in items]


class CodeItemSerializer(CodeSerializer):
    paid = serializers.SerializerMethodField()

    def get_paid(self, _):
        return self.context.get("paid")

    class Meta:
        model = Code
        fields = ("id", "name", "status", "decryption", "image", "paid")


class CodeTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTax
        fields = "__all__"

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
