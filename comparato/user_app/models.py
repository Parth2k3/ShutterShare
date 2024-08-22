from django.db import models
from django.contrib.auth.models import AbstractUser
from home.models import Comments, Image, Posts

class User(AbstractUser):
    TOPICS = (
        ('Self-Portraits', "Self-Portraits"),
        ('Art', 'Art'),
        ('Fashion & Style','Fashion & Style'),
        ('Products', 'Products'),
        ('Creative Projects', 'Creative Projects'),
        ('Events', 'Events'),
        ('Photography Techniques', 'Photography Techniques'),
        ('Themes & Challenges', 'Themes & Challenges'),
        ('Inspiration & Ideas', 'Inspiration & Ideas'),
        ('Comparisons', 'Comparisons')
    )
    first_name = models.CharField(max_length=155, blank=True, null=True)
    last_name = models.CharField(max_length=155, blank=True, null=True)
    user_pic = models.FileField(upload_to='ProfilePic', blank=True, null=True)
    bio = models.CharField(max_length=100, blank=True, null=True)
    followers = models.ManyToManyField('user_app.user', related_name='user_followers', blank=True)
    following = models.ManyToManyField('user_app.user', related_name='user_following', blank=True)
    sugg1 = models.CharField(choices=TOPICS, blank=True, null=True)
    sugg2 = models.CharField(choices=TOPICS, blank=True, null=True)
    sugg3 = models.CharField(choices=TOPICS, blank=True, null=True)
    sugg4 = models.CharField(choices=TOPICS, blank=True, null=True)
    yang = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    details_provided = models.BooleanField(default=False)
    website = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)

    
    def total_posts(self):
        return Posts.objects.filter(creator = self).count()
    def images_uploaded(self):
        return Image.objects.filter(creator=self).count()
    def total_votes(self):
        total_votes = 0
        total_votes += Image.objects.filter(likers=self).count()
        return total_votes
    def total_comments(self):
        posts = Posts.objects.filter(creator = self)
        return sum(post.comment_count() for post in posts)
    def total_likes(self):
        posts = Posts.objects.filter(creator = self)
        return sum(post.like_count() for post in posts)
    