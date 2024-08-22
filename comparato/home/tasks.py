from celery import shared_task
import cloudinary.uploader
from .models import Image, Posts
from user_app.models import User

@shared_task
def upload_image_to_cloudinary(posted_images, user_id, post_id):
    post = Posts.objects.get(id=post_id)
    user = User.objects.get(id=user_id)
    
    for img in posted_images:
        result = cloudinary.uploader.upload(img)
        image_instance = Image.objects.create(
            image_file=result['url'], 
            creator=user
        )
        post.images.add(image_instance)