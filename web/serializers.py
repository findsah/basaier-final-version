# from .models import SuperUser
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from web.views import create_user
from news.models import Profile
from news.models import Slider, PRNews, PRCategory, \
    ScienceCategory, ScienceNews
from projects.models import Project, Category, \
    Transaction, Donate, ProjectsDirectory, SMS, Sacrifice, sponsorship, sponsorshipProjects, sponsorshipPageContent, \
    CompaignCategory, Compaigns


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone']
        extra_kwargs = {
            'first_name': {'required': True},
            # 'phone': {'required': True}
        }

    def validate_email(self, value):
        """
        Check that the valid email with @gmail.com is provided by the user or not in the given email.
            """
        data = self.get_initial()
        email = data.get('email')
        # password = value
        # user_email = User.objects.filter(email=email)
        user_email = User.objects.filter(email=email)

        if user_email:
            raise ValidationError("User With This Email Already Exists.")
            # return False
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        # user = User.objects.create(
        #     username=validated_data['username'],
        #     email=validated_data['email'],
        #     phone=validated_data['phone'],
        #     # last_name=validated_data['last_name']
        # )
        user = create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            # name=validated_data['username'],
            phone=validated_data['phone']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)
    # token = serializers.CharField(
    #     label=_("Token"),
    #     read_only=True
    # )


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('__all__')


class slidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ('__all__')


class project_dirctoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsDirectory
        fields = ('__all__')


class newsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PRNews
        fields = ('__all__')


class science_newsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScienceNews
        fields = ('__all__')


class categoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PRCategory
        fields = ('__all__')


class sponsorCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = sponsorship
        fields = ('__all__')


class sponsorshipProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = sponsorshipProjects
        fields = ('__all__')


class charity_categoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')


class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('__all__')
