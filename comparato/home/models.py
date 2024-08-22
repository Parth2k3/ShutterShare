from django.db import models
from utils.abstract_models import TimestampedModel

class Comments(TimestampedModel):
    text = models.CharField(max_length=255, blank=True, null=True)

class Topic(models.Model):
    self_portraits = models.FloatField(default=0.00)
    art = models.FloatField(default=0.00)
    fashion_style = models.FloatField(default=0.00)
    products = models.FloatField(default=0.00)
    creative_projects = models.FloatField(default=0.00)
    events = models.FloatField(default=0.00)
    photography_techniques = models.FloatField(default=0.00)
    themes_challenges = models.FloatField(default=0.00)
    inspiration_ideas = models.FloatField(default=0.00)
    comparisons = models.FloatField(default=0.00)
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, related_name='post_topics', blank=True)

class Posts(TimestampedModel):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    comments = models.ManyToManyField('Comments', related_name='post_comments', blank=True)
    likers = models.ManyToManyField('user_app.user', related_name='post_likers', blank=True)
    images = models.ManyToManyField('Image', related_name='post_images', blank=True)
    is_private = models.BooleanField(default=True)
    
    def like_count(self):
        cnt = self.likers.count()
        return cnt if cnt != 0 else 0

    def comment_count(self):
        return self.comments.count()

    def total_votes(self):
        return sum(cnt.likes for cnt in self.images.all())

    def get_full_name(self):
        if(self.creator):
            return self.creator.first_name + self.creator.last_name
        else:
            return "none"

class Image(TimestampedModel):
    image_file = models.CharField(max_length=765, blank=True, null=True)
    likes = models.IntegerField(default=0)
    likers = models.ManyToManyField('user_app.user', related_name='image_likers', blank=True)
    title = models.CharField(max_length=100, blank=True, null=True)

class Notifs(TimestampedModel):
    messages = models.CharField(max_length=255, blank=True, null=True)
    target = models.ForeignKey('user_app.user',on_delete=models.CASCADE, related_name="notif_user",null=True, blank=True)
    is_read = models.BooleanField(default=False)
    url = models.CharField(max_length=255, default='#')