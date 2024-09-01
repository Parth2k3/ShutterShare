from rest_framework import serializers
from .models import Posts, Image, Topic

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_file', 'title']

class PostTopicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'self_portraits', 'art', 'fashion_style', 'products', 'creative_projects', 'events', 'photography_techniques', 'themes_challenges', 'inspiration_ideas', 'comparisons']

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    post_topics = PostTopicsSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = ['id', 'title', 'description', 'privacy', 'images', 'post_topics', 'like_count', 'comment_count', 'creator', 'created', 'modified']

    def get_like_count(self, obj):
        return obj.likers.count()

    def get_comment_count(self, obj):
        return obj.comments.count()
