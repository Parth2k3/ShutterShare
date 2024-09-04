from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, render, get_object_or_404
from .models import Posts, Topic, Image, Comments, Notifs
from .vector import generate_and_store_embeddings, get_related_posts
from comparato.permissions import CustomIsAuthenticated
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
        is_related = request.GET.get('related', 'false').lower() == 'true'
        
        if search_query:
            posts = Posts.objects.filter(
                Q(is_private=False) | Q(creator__in=request.user.following.all()) | Q(creator=request.user),
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            ).prefetch_related('post_topics').order_by('-id')
        else:
            posts = get_related_posts(request.user)
        # else:
        #     posts = Posts.objects.filter(
        #         Q(is_private=False) | Q(creator__in=request.user.following.all()) | Q(creator=request.user)
        #     ).prefetch_related('post_topics').order_by('-id')
            
        paginator = Paginator(posts, 6)
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
import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PILImage

def decode_base64_file(data):
    try:
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    except ValueError as e:
        print("Error splitting Base64 string:", e)
        return None

from io import BytesIO

class CreatePostView(APIView):
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        posted_data = request.data
        post = Posts.objects.create(
            title=posted_data.get('title'),
            description=posted_data.get('desc') if 'desc' in posted_data else None,
            is_private=posted_data.get('privacy') == 'followers',
            creator=request.user
        )

        for base64_image in request.POST.getlist('cropped_images[]'):
            img_data = decode_base64_file(base64_image)

            if img_data is not None:
                # Convert PIL image to bytes
                img = PILImage.open(img_data)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                # Upload the image to Cloudinary
                result = cloudinary.uploader.upload(img_byte_arr)

                # Create Image instance and associate it with the post
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
            Notifs.objects.create(
                creator=request.user,
                target=follower,
                messages='has made a new post.',
                url=f"/view/{post.id}"
            )

        generate_and_store_embeddings(post)
        return redirect("index")


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

import re

@login_required
@api_view(['POST'])
def delete_post(request, post_id):
    post = Posts.objects.get(id=post_id)
    if request.user == post.creator:
        for image in post.images.all():
            cloudinary_url = image.image_file
            public_id = extract_public_id(cloudinary_url)
            destroy(public_id)
            image.delete()
        post.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({"status": "failed"})

def extract_public_id(cloudinary_url):
    # Regex to extract the public_id from the Cloudinary URL
    match = re.search(r'/v\d+/(.+)\.\w+$', cloudinary_url)
    if match:
        return match.group(1)
    return None