from rest_framework import serializers

from .models import *


class CodesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, code):
        if code.image:
            return code.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Code
        fields = ("id", "name", "status", "decryption", "image")


class CodeSerializer(CodesSerializer):
    class Meta(CodesSerializer.Meta):
        fields = "__all__"


class TaxsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tax
        fields = "__all__"


class TaxSerializer(TaxsSerializer):
    codes = serializers.SerializerMethodField()
            
    def get_codes(self, tax):
        items = CodeTax.objects.filter(tax=tax)

        if tax.status == 3:
            return [CodeItemSerializer(item.code, context={"summ": item.summ}).data for item in items]

        return [CodeSerializer(item.code).data for item in items]


class CodeItemSerializer(CodeSerializer):
    summ = serializers.SerializerMethodField()

    def get_summ(self, _):
        return self.context.get("summ")


class CodeTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTax
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


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
