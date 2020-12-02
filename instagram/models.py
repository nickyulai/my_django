from django.db import models
import datetime


# Create your models here.
class IGAcoount(models.Model):
    user_name = models.CharField(max_length=100, blank=False)
    email = models.CharField(max_length=200, blank=False)
    password = models.CharField(max_length=200, blank=False)
    session_id = models.CharField(max_length=600, blank=False)
    cookie = models.CharField(max_length=600, blank=False)
    last_update = models.DateTimeField('last_update')
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'IG爬蟲帳號'
        verbose_name_plural = 'IG爬蟲帳號'
        db_table = 'ig_accounts'


class InstagramList(models.Model):
    user_name = models.CharField(max_length=100, blank=False)
    cname = models.CharField(max_length=75, default=None, blank=True, null=True)
    last_update = models.DateTimeField(default=datetime.datetime.now, blank=True)
    scrap_post = models.DateTimeField(default=datetime.datetime.now, blank=True)
    get_attached = models.BooleanField(default=False)
    get_comments_uid = models.BooleanField(default=False)
    # send_tg = models.BooleanField(default=False)
    admin = models.ForeignKey('IGAcoount', related_name='instagrams', on_delete=models.SET_NULL, null=True, blank=True)
    actived = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'IG列表'
        verbose_name_plural = 'IG列表'
        db_table = 'instagram_list'


class InstagramProfile(models.Model):
    user_name = models.CharField(max_length=100, blank=False)
    profile_name = models.CharField(max_length=100, blank=True, null=True)
    profile_url = models.URLField(max_length=500, blank=True, null=True)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)
    bio = models.TextField(blank=False)
    profile_pic_url = models.URLField(max_length=500, blank=True, null=True)
    is_business_account = models.BooleanField(default=False)
    connected_to_fb = models.CharField(max_length=100, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    scraped_time = models.DateTimeField('scraped_time', auto_now_add=True)

    class Meta:
        verbose_name = 'IG個資'
        verbose_name_plural = 'IG個資'
        db_table = 'Instagram_profile'


class InstagramPosts(models.Model):
    user_name = models.CharField(max_length=100, blank=False)
    post_url = models.URLField(max_length=2000, blank=True, null=True)
    post_type = models.CharField(max_length=100, blank=False)
    post_message = models.TextField(blank=False)
    comments_disable = models.BooleanField(default=False)
    comments = models.IntegerField(default=0)
    interactions = models.IntegerField(default=0)
    created_time = models.DateTimeField('created_time', null=True)
    pic_or_video_url = models.CharField(max_length=3000, blank=True)
    scraped_time = models.DateTimeField('scraped_time', auto_now_add=True)

    class Meta:
        verbose_name = 'IG貼文'
        verbose_name_plural = 'IG貼文'
        db_table = 'instagram_posts'


class InstagramComments(models.Model):
    post_url = models.URLField(max_length=2000, blank=True, null=True)
    user_name = models.CharField(max_length=100, blank=False)
    comment_message = models.TextField(blank=False)
    created_time = models.DateTimeField('created_time', null=True)
    scraped_time = models.DateTimeField('scraped_time', auto_now_add=True)

    class Meta:
        verbose_name = 'IG留言'
        verbose_name_plural = 'IG留言'
        db_table = 'instagram_comments'
