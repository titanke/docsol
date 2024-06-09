import os
import time
import uuid
import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, Http404
from django.conf import settings
from home.models import FileInfo, Task
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
import shutil
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden

from home.forms import TaskForm
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404

def index(request):

    context = {}

    # Add context data here
    # context['test'] = 'OK'

    # Page from the theme 
    return render(request, 'pages/dashboard.html', context=context)

def custom_403_view(request, exception=None):
    return render(request, 'layouts/403.html', status=403)

##
def tasks(request):
    todo = Task.objects.all()    
    if request.method == 'POST':
        form=TaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            instance.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form=TaskForm()
    context={'todo':todo,'form':form}
    return render(request, 'pages/index.html',context)


def update(request,pk):
    todo=Task.objects.get(id=pk)
    form=TaskForm(instance=todo)
    if request.method=='POST':
       form= TaskForm(request.POST,instance=todo)
       if form.is_valid():
            instance = form.save(commit=True)
            instance.save()
            return redirect(tasks)
    context={'form':form}
    return render(request, 'pages/update.html', context)
    
def delete(request,pk):
    try:
        todo=Task.objects.get(id=pk)
        todo.delete()
        return redirect(tasks)
    except Task.DoesNotExist:
        return HttpResponse("Task not found.", status=404)

def completed(request,pk):
    todo=Task.objects.get(pk=pk)
    todo.completed=True
    todo.save()
    return redirect(request.META.get('HTTP_REFERER'))

def uncompleted(request,pk):
    todo=Task.objects.get(pk=pk)
    todo.completed=False
    todo.save()
    return redirect(request.META.get('HTTP_REFERER'))


##

def convert_csv_to_text(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    text = ''
    for row in rows:
        text += ','.join(row) + '\n'

    return text

def get_files_from_directory(directory_path):
    files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                print( ' > file_path ' + file_path)
                _, extension = os.path.splitext(filename)
                if extension.lower() == '.csv':
                    csv_text = convert_csv_to_text(file_path)
                else:
                    csv_text = ''
                # Recupera la fecha y hora de subida de los metadatos del archivo
                upload_date = time.strftime('%d/%m/%Y %H:%M', time.localtime(os.path.getmtime(file_path)))   
                files.append({
                    'file': file_path.split(os.sep + 'media' + os.sep)[1],
                    'filename': filename,
                    'file_path': file_path,
                    'csv_text': csv_text,
                    'upload_date': upload_date,
                    'username': upload_date  # Agrega el nombre del usuario a la información del archivo
                })
            except Exception as e:
                print( ' > ' +  str( e ) )    
    return files

def save_info(request, file_path):
    path = file_path.replace('%slash%', '/')
    if request.method == 'POST':
        FileInfo.objects.update_or_create(
            path=path,
            defaults={
                'info': request.POST.get('info')
            }
        )
    
    return redirect(request.META.get('HTTP_REFERER'))

def get_breadcrumbs(request):
    path_components = [component for component in request.path.split("/") if component]
    breadcrumbs = []
    url = ''

    for component in path_components:
        url += f'/{component}'
        if component == "file-manager":
            component = "media"
        breadcrumbs.append({'name': component, 'url': url})

    return breadcrumbs

@login_required(login_url='/accounts/login/')
def file_manager(request, directory=''):
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'pages/file-manager.html', context)




def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    return directories


def delete_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(absolute_file_path)
    print("File deleted", absolute_file_path)
    return redirect(request.META.get('HTTP_REFERER'))

    
def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404

def upload_file(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    selected_directory = request.POST.get('directory', '') 
    selected_directory_path = os.path.join(media_path, selected_directory)
    if request.method == 'POST':
        file = request.FILES.get('file')
        file_path = os.path.join(selected_directory_path, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        # Guarda la fecha y hora de subida en los metadatos del archivo
        os.utime(file_path, times=(time.time(), time.time()))
        username = request.user.username  # Obtiene el nombre de usuario

    return redirect(request.META.get('HTTP_REFERER'))

def mk_dir(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    selected_directory = request.POST.get('directory', '') 
    folder_name = request.POST.get('folder_name', '') 
    folder_path = os.path.join(media_path, selected_directory, folder_name)
    if request.method == 'POST':
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Redirige al directorio recién creado
    return redirect(request.META.get('HTTP_REFERER'))


def delete_dir(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    selected_directory = request.POST.get('directory', '') 
    folder_path = os.path.join(media_path, selected_directory)
    print(folder_path)
    if request.method == 'POST':
        try:
            if os.path.exists(folder_path):
                # Verifica si el nombre de la carpeta es "media"
                if selected_directory.lower() != '':
                    shutil.rmtree(folder_path)
                else:
                    print("No se puede borrar la carpeta 'media'.")
        except Exception as e:
            print(f"Error al eliminar el directorio: {e}")

    return redirect("/file-manager")


