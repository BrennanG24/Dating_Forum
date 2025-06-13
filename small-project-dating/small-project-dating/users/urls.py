from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'), 
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/login.html', next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),  # Profil sayfası
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Profil düzenleme sayfası
    path('blog/new/', views.create_blog_post, name='create_blog_post'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),  # Blog detay URL'i
    path('users/', views.user_list, name='user_list'),
    path('search/', views.search_profiles, name='search_profiles'),
    path('message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('profile/picture/', views.update_profile_picture, name='update_profile_picture'),
    path('message/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
] 