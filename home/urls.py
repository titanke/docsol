from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('file-manager/', views.file_manager, name='file_manager'),
    re_path(r'^file-manager/(?P<directory>.*)?/$', views.file_manager, name='file_manager'),
    path('delete-file/<str:file_path>/', views.delete_file, name='delete_file'),
    path('download-file/<str:file_path>/', views.download_file, name='download_file'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('mk-dir/', views.mk_dir, name='mk_dir'),
    path('delete-dir/', views.delete_dir, name='delete_dir'),
    path('save-info/<str:file_path>/', views.save_info, name='save_info'),
    path('download_all/', views.download_all, name='download_all'),

    
    path('task/', views.tasks, name='task'),
    path('<int:pk>', views.delete, name='delete'),
    path('<int:pk>/completed/', views.completed, name='completed'),
    path('<int:pk>/uncompleted/', views.uncompleted, name='uncompleted'),
    path('<int:pk>/update/', views.update, name='update')

]
