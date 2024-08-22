from django.urls import path
from home.views import IndexView, CreatePostView, CompareView, thanks, comment, like_post, ViewView, update_post, delete_image, PeopleView, follow, remove_follow, read_notification, delete_post

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('compare/<int:post_id>', CompareView.as_view(), name='compare'),
    path('compare/vote/<int:image_id>/', CompareView.as_view(), name='vote'),
    path('thanks/<int:post_id>', thanks, name='thank'),
    path('comment/<int:post_id>', comment, name='comment'),
    path('like_post/<int:post_id>', like_post, name='like_post'),
    path('view/<int:post_id>', ViewView.as_view(), name='view_post'),
    path('update_post/<int:post_id>', update_post, name='update_post'),
    path('delete_image/<int:image_id>', delete_image, name='delete_image'),
    path('followers/', PeopleView.as_view(), name='people_view'),
    path('follow/<int:user_id>', follow, name='follow'),
    path('remove_follow/<int:user_id>', remove_follow, name='remove_follow'),
    path('read_notification/', read_notification, name='read_notification'),
    path('delete_post/<int:post_id>', delete_post, name='delete_post'),
]