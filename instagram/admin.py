# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.db import models
from django.forms import Textarea
from import_export.admin import ImportExportActionModelAdmin
from rangefilter.filter import DateRangeFilter

from instagram.models import IGAcoount, InstagramList, InstagramProfile, InstagramPosts, InstagramComments


class IGAccountAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'password', 'last_update', 'active')
    search_fields = ('user_name', 'email',)


class InstagramListAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'cname', 'actived', 'admin')
    search_fields = ('user_name', )
    raw_id_fields = ('admin', )


class InstagramProfileAdmin(ImportExportActionModelAdmin):
    list_display = ('user_name', 'bio', 'followers', 'following',
                    'scraped_time', 'is_private', 'is_verified', )
    search_fields = ('user_name', )


class InstagramPostsAdmin(ImportExportActionModelAdmin):
    list_display = ('user_name', 'post_message', 'interactions',
                    'comments', 'comments_disable', 'created_time', 'scraped_time', )
    search_fields = ('user_name', )
    list_filter = (('scraped_time', DateRangeFilter),
                   ('created_time', DateRangeFilter))


class InstagramCommentsAdmin(ImportExportActionModelAdmin):
    list_display = ('post_url', 'user_name', 'comment_message',
                    'created_time', 'scraped_time', )
    search_fields = ('post_url', 'user_name')
    list_filter = (('scraped_time', DateRangeFilter),
                   ('created_time', DateRangeFilter))


admin.site.register(IGAcoount, IGAccountAdmin)
admin.site.register(InstagramList, InstagramListAdmin)
admin.site.register(InstagramProfile, InstagramProfileAdmin)
admin.site.register(InstagramPosts, InstagramPostsAdmin)
admin.site.register(InstagramComments, InstagramCommentsAdmin)
