from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from user_app.models import User
from home.models import Posts, Notifs

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print('wow')
            login(request, user)
            if user.details_provided:
                return redirect('index')
            return redirect('details')
        else:
            print('sad')
            return render(request, 'user_app/login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'user_app/login.html')


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('pass1')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('details')  
    return render(request, 'user_app/register.html')

def details(request):

    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        yang = request.POST['yang']
        bio = request.POST['bio']
        picture = request.FILES['picture']
        topics = request.POST.getlist('topics[]')
        user = request.user
        user.first_name = fname
        user.last_name = lname
        user.user_pic = picture
        user.bio = bio
        user.yang = yang
        user.sugg1 = topics[0] if len(topics) > 0 else None
        user.sugg2 = topics[1] if len(topics) > 1 else None
        user.sugg3 = topics[2] if len(topics) > 2 else None
        user.sugg4 = topics[3] if len(topics) > 3 else None
        user.details_provided = True
        user.save()

        

        return redirect('index')

    else:
        if not request.user:
            return redirect('index')
        elif request.user.details_provided:
            return redirect('index')
        else:
            return render(request, "user_app/user_details.html")

def logout_view(request):
    logout(request)
    return redirect('login_view')

def profile(request, username):

  if request.method == "POST":
    data = request.POST
    user = request.user
    for key, value in data.items():
        if key != 'user_pic':
            setattr(user, key, value)
    
    if data['user_pic'] != '':
        user.user_pic = data['user_pic']
    user.save()
    return redirect('profile', username=request.user.username)

  else:  
    user = get_object_or_404(User, username=username)
    posts = Posts.objects.filter(creator = user).order_by('-created')
    if(request.user == user):
        edit_access = True
    else:
        edit_access = False
    
    if edit_access == False:
        notif = Notifs.objects.create(
            creator = request.user,
            target = user,
            messages = 'visited your profile.',
            url = f"/profile/{request.user.username}"
        )
    context = {
        'user': user,
        'edit_access':edit_access,
        'posts': posts,
    }
    return render(request, "user_app/profile.html", context=context)

def dash(request):
    posts = Posts.objects.filter(creator = request.user)
    context = {
        'posts': posts
    }
    return render(request, "user_app/dashboard.html", context=context)