from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class SlashedUsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w.@+-/]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )

class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[SlashedUsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    course = models.ForeignKey('timetabling.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    must_change_password = models.BooleanField(default=False, help_text="Force user to change password on next login.")
    year = models.IntegerField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True, default=1)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # If the user is a lecturer and being created (no password), we can set a default
        if self.role == 'lecturer' and not self.password:
            self.set_password(self.username)
            self.must_change_password = False
            self.is_staff = True  # Ensure they can log in if needed, or based on your RBAC

        # Set default password for students (username IS the password)
        # We enforce this on creation to satisfy the requirement
        if self.role == 'student' and (is_new or not self.password):
            self.set_password(self.username)
            self.must_change_password = False  # username is their default password

        # Auto-assign course for students based on username prefix if no course is set
        if self.role == 'student' and not self.course:
            username_upper = self.username.upper().replace(' ', '')
            from timetabling.models import Course
            if username_upper.startswith('CCS'):
                self.course = Course.objects.filter(name__icontains='Computer Science').first()
            elif username_upper.startswith('CCT'):
                self.course = Course.objects.filter(name__icontains='Computer Technology').first()

        # Auto-assign year for students based on suffix if not set
        if self.role == 'student' and not self.year:
            username_clean = self.username.strip()
            # logic: /025 -> Yr 1 (2025 entry), /024 -> Yr 2, etc. (relative to 2025/2026 academic year)
            if '/025' in username_clean:
                self.year = 1
            elif '/024' in username_clean:
                self.year = 2
            elif '/023' in username_clean:
                self.year = 3
            elif '/024' in username_clean: # Fix potential typo if detected
                 self.year = 2
            elif '/021' in username_clean:
                self.year = 4

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"