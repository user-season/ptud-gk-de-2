from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from .models import Task
from .models import Profile


# Trang chủ
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'taskApp/login.html')


# Đăng ký người dùng
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        error = False
        
        # Kiểm tra xác nhận mật khẩu
        if password1 != password2:
            messages.error(request, 'Mật khẩu không khớp.')
            error = True
        
        # Kiểm tra tên người dùng đã tồn tại
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            error = True
            
        # Kiểm tra email đã tồn tại
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại.')
            error = True
        
        if not error:
            # Tạo người dùng mới
            user = User(
                username=username,
                email=email,
                password=make_password(password1)
            )
            user.save()
            
            messages.success(request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.')
            return redirect('login')
    
    return render(request, 'taskApp/register.html')


# Đăng nhập
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Chào mừng, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác.')
    
    return render(request, 'taskApp/login.html')


# Đăng xuất
def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')


# Bảng điều khiển
@login_required
def dashboard(request):
    # Người dùng xem công việc của mình
    tasks = Task.objects.filter(author=request.user)
    
    context = {
        'tasks': tasks,
        'pending_count': tasks.filter(status='pending').count(),
        'in_progress_count': tasks.filter(status='in_progress').count(),
        'completed_count': tasks.filter(status='completed').count(),
        'cancelled_count': tasks.filter(status='cancelled').count(),
    }
    return render(request, 'taskApp/dashboard.html', context)


# Danh sách công việc
@login_required
def task_list(request):
    # Người dùng chỉ xem công việc của mình
    tasks = Task.objects.filter(author=request.user)
    
    return render(request, 'taskApp/task_list.html', {'tasks': tasks})


# Chi tiết công việc
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Kiểm tra quyền xem công việc
    if task.author != request.user:
        messages.error(request, 'Bạn không có quyền xem công việc này.')
        return redirect('dashboard')
    
    return render(request, 'taskApp/task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        target_date = request.POST.get('target_date')
        
        if not all([title, description, status]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return render(request, 'taskApp/task_create.html', {
                'status_choices': Task.STATUS_CHOICES,
                'is_new': True
            })
        
        try:
            task = Task(
                title=title,
                description=description,
                status=status,
                author=request.user,
            )
            
            # Xử lý target_date nếu được cung cấp
            if target_date:
                try:
                    # Chuyển đổi chuỗi ngày thành đối tượng date
                    task.target_date = target_date
                except ValueError:
                    messages.warning(request, 'Định dạng ngày mục tiêu không hợp lệ. Đã bỏ qua trường này.')
            
            task.save()
            
            messages.success(request, 'Tạo công việc mới thành công!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi tạo công việc: {str(e)}')
    
    return render(request, 'taskApp/task_create.html', {
        'status_choices': Task.STATUS_CHOICES,
        'is_new': True
    })


# Cập nhật công việc
@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Kiểm tra quyền cập nhật: chỉ người tạo hoặc admin
    # if task.author != request.user and not request.user.is_staff:
    #     messages.error(request, 'Bạn không có quyền cập nhật công việc này.')
    #     return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        
        if not all([title, description, status]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return render(request, 'taskApp/task_update.html', {
                'task': task,
                'status_choices': Task.STATUS_CHOICES,
                'is_new': False
            })
        
        task.title = title
        task.description = description
        task.status = status
        
        # Nếu trạng thái là hoàn thành, cập nhật ngày hoàn thành
        if status == 'completed' and not task.finished:
            task.finished = timezone.now()
        
        task.save()
        messages.success(request, 'Cập nhật công việc thành công!')
        return redirect('task_detail', task_id=task.id)
    
    return render(request, 'taskApp/task_update.html', {
        'task': task,
        'status_choices': Task.STATUS_CHOICES,
        'is_new': False
    })


# Xóa công việc
@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Kiểm tra quyền xóa: chỉ người tạo hoặc admin
    if task.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa công việc này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Xóa công việc thành công!')
        return redirect('task_list')
    
    return render(request, 'taskApp/task_confirm_delete.html', {'task': task})



@login_required
def profile_view(request):
    """Hiển thị và cập nhật thông tin cá nhân của người dùng"""
    user = request.user
    
    if request.method == 'POST':
        # Cập nhật thông tin cá nhân
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Cập nhật profile
        user.profile.bio = request.POST.get('bio', '')
        user.profile.phone = request.POST.get('phone', '')
        
        # Xử lý upload avatar
        if 'avatar' in request.FILES:
            user.profile.avatar = request.FILES['avatar']
        
        user.profile.save()
        messages.success(request, 'Cập nhật thông tin cá nhân thành công!')
        return redirect('profile')
    
    return render(request, 'taskApp/profile.html', {'user': user})

@login_required
def change_password(request):
    """Thay đổi mật khẩu"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Kiểm tra mật khẩu hiện tại
        if not request.user.check_password(current_password):
            messages.error(request, 'Mật khẩu hiện tại không chính xác.')
            return redirect('change_password')
        
        # Kiểm tra mật khẩu mới và xác nhận
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận không khớp.')
            return redirect('change_password')
        
        # Thay đổi mật khẩu
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Thay đổi mật khẩu thành công! Vui lòng đăng nhập lại.')
        return redirect('login')
    
    return render(request, 'taskApp/change_password.html')