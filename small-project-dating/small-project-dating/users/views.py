from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm, BlogPostForm, MessageForm, ProfilePictureForm
from .models import BlogPost, UserProfile, Message, User
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Q

# Create your views here.

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'users/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.user = request.user
            blog_post.save()
            messages.success(request, 'Your blog post has been created!')
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'users/blog_post.html', {'form': form})

@login_required
def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'users/blog_list.html', {'posts': posts})

@login_required
def user_list(request):
    # Update online status for all users
    offline_threshold = now() - timedelta(minutes=5)
    UserProfile.objects.filter(last_seen__lt=offline_threshold).update(is_online=False)
    
    # Get all user profiles except superusers
    profiles = UserProfile.objects.select_related('user').exclude(user__is_superuser=True)
    return render(request, 'users/user_list.html', {'profiles': profiles})

@login_required
def search_profiles(request):
    query_gender = request.GET.get('gender', '')
    query_min_age = request.GET.get('min_age', '')
    query_max_age = request.GET.get('max_age', '')
    query_career = request.GET.get('career', '')
    query_min_income = request.GET.get('min_income', '')

    # Başlangıçta superuser olmayanları filtrele
    results = UserProfile.objects.exclude(user__is_superuser=True)

    if query_gender:
        results = results.filter(gender=query_gender)
    if query_min_age:
        results = results.filter(age__gte=query_min_age)
    if query_max_age:
        results = results.filter(age__lte=query_max_age)
    if query_career:
        results = results.filter(career__icontains=query_career)
    if query_min_income:
        results = results.filter(income__gte=query_min_income)

    # Update online status
    offline_threshold = now() - timedelta(minutes=5)
    UserProfile.objects.filter(last_seen__lt=offline_threshold).update(is_online=False)

    return render(request, 'users/search_results.html', {
        'results': results,
        'query_gender': query_gender,
        'query_min_age': query_min_age,
        'query_max_age': query_max_age,
        'query_career': query_career,
        'query_min_income': query_min_income,
    })

@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('inbox')
    else:
        form = MessageForm()
    
    return render(request, 'users/send_message.html', {
        'form': form,
        'receiver': receiver
    })

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    unread_messages_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    return render(request, 'users/inbox.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
        'unread_messages_count': unread_messages_count
    })

@login_required
def update_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('user_list')
    else:
        form = ProfilePictureForm(instance=request.user.userprofile)
    
    return render(request, 'users/update_profile_picture.html', {'form': form})

@login_required
def mark_message_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.is_read = True
    message.save()
    return redirect('inbox')

def home(request):
    # En son aktif olan 3 kullanıcıyı al (superuser hariç)
    featured_profiles = UserProfile.objects.select_related('user').exclude(user__is_superuser=True).order_by('-last_seen')[:3]
    
    # En son eklenen 3 blog yazısını al (superuser hariç)
    latest_blogs = BlogPost.objects.select_related('user').exclude(user__is_superuser=True).order_by('-created_at')[:3]
    
    # Okunmamış mesaj kontrolü
    has_unread_messages = False
    if request.user.is_authenticated:
        has_unread_messages = Message.objects.filter(receiver=request.user, is_read=False).exists()
    
    context = {
        'featured_profiles': featured_profiles,
        'latest_blogs': latest_blogs,
        'has_unread_messages': has_unread_messages,
    }
    return render(request, 'users/home.html', context)

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Profil bilgilerini güncelle
        profile = request.user.userprofile
        profile.age = request.POST.get('age') or None
        profile.gender = request.POST.get('gender') or None
        profile.height = request.POST.get('height') or None
        profile.career = request.POST.get('career') or None
        profile.income = request.POST.get('income') or None
        profile.location = request.POST.get('location') or None
        profile.contact_info = request.POST.get('contact_info') or None
        profile.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    return render(request, 'users/edit_profile.html')

@login_required
def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'users/blog_detail.html', {'post': post})
