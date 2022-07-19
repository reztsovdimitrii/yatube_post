from .models import Post

from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('text', 'pub_date', 'author', 'group', 'image')
