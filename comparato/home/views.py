from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, render, get_object_or_404
from .models import Posts, Topic, Image, Comments, Notifs
# from .vector import main
from comparato.permissions import CustomIsAuthenticated
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
import datetime
from django.db.models import Q
from user_app.models import User
import cloudinary.uploader
from cloudinary.uploader import destroy
from django.core.paginator import Paginator

class IndexView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        search_query = request.GET.get('q', '').strip()
        page_number = request.GET.get('page', 1)
        
        # Filter posts based on the search query
        posts = Posts.objects.filter(
            Q(is_private=False) | Q(creator__in=request.user.following.all()) | Q(creator=request.user),
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        ).prefetch_related('post_topics').order_by('-id')

        # Paginate posts
        paginator = Paginator(posts, 4)  # Show 7 posts per page
        page_obj = paginator.get_page(page_number)

        for post in page_obj:
            post.comment_count = post.comments.count()

        notifications = Notifs.objects.filter(
            Q(target=request.user) & ~Q(creator=request.user)
        ).order_by('-created')
        
        context = {
            'posts': page_obj,
            'notifications': notifications
        }
        return render(request, "home/index.html", context=context)

import cloudinary.uploader

class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        posted_data = request.data
        posted_images = request.FILES.getlist('image')
        post = Posts.objects.create(
            title = posted_data.get('title'),
            description = posted_data.get('desc') if 'desc' in posted_data else None,
            is_private = posted_data.get('privacy') == 'followers',
            creator = request.user
        )
        for img in posted_images:
            result = cloudinary.uploader.upload(img)
            image_instance = Image.objects.create(
                image_file=result['url'], 
                creator=request.user
            )
            post.images.add(image_instance)

        for tag in posted_data.getlist('tags[]'):
            topic, created = Topic.objects.get_or_create(post=post)
            setattr(topic, tag, 1.0)
            topic.save()
        for follower in request.user.followers.all():
            notif = Notifs.objects.create(
                creator = request.user,
                target = follower,
                messages = 'has made a new post.',
                url = f"/view/{post.id}"
            )
        return redirect("index")

class UploadProgressView(APIView):
    permission_classes = [CustomIsAuthenticated]

    async def get(self, request):
        user_id = request.user.id
        progress = cache.get(f'upload_progress_{user_id}', 0)
        return JsonResponse({'progress': progress})


class CompareView(APIView):
    def get(self, request, post_id):
        user_post = Posts.objects.get(id = post_id)
        images = user_post.images.all()
        images_data = [{'id': image.id, 'url': image.image_file} for image in images]
        context = {
            'post': user_post,
            'images': images_data
        }
        return render(request, "home/compare.html", context=context)
    def post(self, request, image_id):
        try:
            image = Image.objects.get(id = image_id)
            image.likes += 1
            if request.user.is_authenticated:
                image.likers.add(request.user)
            image.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Image not found'})
        

def thanks(request, post_id):
    post = Posts.objects.get(id=post_id)
    if request.user.is_authenticated:
        notif = Notifs.objects.create(
            creator = request.user,
            target = post.creator,
            messages = f'did a comparison for your post {post.title}',
            url = f"/view/{post.id}"
        )
    else:
        notif = Notifs.objects.create(
            target = post.creator,
            messages = f'Somebody anonymously did a comparison for your post {post.title}',
            url = f"/view/{post.id}"
        )
    return render(request, "home/thank.html", context={'post_id': post_id})

@login_required
@api_view(['POST'])
def comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Posts, id=post_id)
        comment_text = request.data.get('comment')
        comment = Comments.objects.create(
            text=comment_text,
            creator=request.user
        )
        post.comments.add(comment)
        post.save()

        notif = Notifs.objects.create(
            creator = request.user,
            target = post.creator,
            messages = f'commented on your post {post.title}',
            url = f"/view/{post.id}"
        )

        return JsonResponse({
            'status': 'success',
            'username': request.user.username
        })

    
@login_required
@api_view(['POST'])
def like_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    
    if request.user in post.likers.all():
        post.likers.remove(request.user)
        liked = False
    else:
        post.likers.add(request.user)
        liked = True
        notif = Notifs.objects.create(
        creator = request.user,
        target = post.creator,
        messages = f'liked your post {post.title}'
        )

    post.save()

    

    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': post.likers.count()
    })

class ViewView(APIView):
    permission_classes = [CustomIsAuthenticated]
    def get(self, request, post_id):
        post = Posts.objects.get(id = post_id)
        context = {
            'post': post
        }
        return render(request, "home/view_post.html", context=context)

@login_required
@api_view(['POST'])
def update_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.description = request.POST.get('description')
        for file in request.FILES.getlist('new_images'):
            result = cloudinary.uploader.upload(file)
            image = Image.objects.create(image_file=result['url'])
            post.images.add(image)
        post.modified = datetime.datetime.now
        post.save()
        return redirect('dash')


@login_required
def delete_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(Image, id=image_id)
        image.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

class PeopleView(APIView):
    permission_classes = [CustomIsAuthenticated]
    def get(self, request):
        return render(request, "home/followers.html")
    
@login_required
@api_view(['POST'])
def follow(request, user_id):
    target = get_object_or_404(User, id=user_id)
    user = request.user

    if (user in target.followers.all()) and (target in user.following.all()):
        user.following.remove(target)
        target.followers.remove(user)
    else:
        user.following.add(target)
        target.followers.add(user)
        notif = Notifs.objects.create(
            creator = user,
            target = target,
            messages = 'is now following you.',
            url = f"/profile/{user}"
        )
    return JsonResponse({'success': True})

@login_required
@api_view(['POST'])
def remove_follow(request, user_id):
    target = get_object_or_404(User, id=user_id)
    user = request.user
    user.followers.remove(target)
    target.following.remove(user)
    return JsonResponse({'success': True})


@login_required
@api_view(['POST'])
def read_notification(request):
    notifications = Notifs.objects.filter(
            Q(target=request.user)
        )
    notifications.update(is_read = True)
    return JsonResponse({'status': 'success'})

@login_required
@api_view(['POST'])
def delete_post(request, post_id):
    post = Posts.objects.get(id=post_id)
    if request.user == post.creator:
        for image in post.images.all():
            cloudinary_id = image.image_file.public_id
            destroy(cloudinary_id)
            image.delete()
        post.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({"status": "failed"})