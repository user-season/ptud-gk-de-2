from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang chờ'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    description = models.TextField(verbose_name="Mô tả")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    finished = models.DateTimeField(null=True, blank=True, verbose_name="Ngày hoàn thành")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="Người tạo")
    target_date = models.DateField(null=True, blank=True, verbose_name="Mục tiêu hoàn thành")
    @property
    def is_late(self):
        """ Kiểm tra xem nhiệm vụ có trễ hạn không """
        if self.status != 'completed' and self.target_date:
            return self.target_date < timezone.localdate()
        return False
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Công việc"
        verbose_name_plural = "Công việc"


from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Người dùng")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Ảnh đại diện")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Giới thiệu")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    
    def __str__(self):
        return f'Hồ sơ của {self.user.username}'
    
    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"
    
    # Phương thức để xóa ảnh cũ khi thay thế bằng ảnh mới
    def save(self, *args, **kwargs):
        if self.id:
            # Nếu đang cập nhật một profile đã tồn tại
            try:
                old_profile = Profile.objects.get(id=self.id)
                if old_profile.avatar and self.avatar != old_profile.avatar:
                    # Nếu có ảnh cũ và ảnh mới khác ảnh cũ
                    if os.path.isfile(old_profile.avatar.path):
                        os.remove(old_profile.avatar.path)
            except (Profile.DoesNotExist, ValueError, FileNotFoundError):
                pass
        super().save(*args, **kwargs)

# Tự động tạo profile khi tạo user mới
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)