from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models


def validate_phone(value):
    """Валидатор для проверки формата телефона."""
    pattern = r"^(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}$"
    if not re.match(pattern, value):
        raise ValidationError("Введите корректный номер телефона.")


def validate_avatar_extension(value):
    """Валидатор для проверки расширения аватара."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    if ext not in valid_extensions:
        raise ValidationError(
            f'Поддерживаются только следующие форматы: {", ".join(valid_extensions)}'
        )


def validate_avatar_size(value):
    """Валидатор для проверки размера аватара."""
    max_size = 2 * 1024 * 1024  # 2 МБ
    if value.size > max_size:
        raise ValidationError("Размер файла не должен превышать 2 МБ")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Пользователи должны иметь email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя должно быть значение is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "У суперпользователя должно быть значение is_superuser=True."
            )

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    """ Модель пользователя """
    email = models.EmailField(
        unique=True,
        verbose_name="Почта",
        help_text="Укажите рабочий email (будет использоваться для входа)",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона в международном формате (+7 XXX XXX-XX-XX)",
        validators=[validate_phone],
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар (форматы: JPG, PNG, GIF; максимум 2 МБ)",
        validators=[validate_avatar_extension, validate_avatar_size],
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Указывает, может ли пользователь войти в систему",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Персонал",
        help_text="Разрешает доступ к админ‑панели",
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Суперпользователь",
        help_text="Предоставляет все права",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )
    tg_chat_id = models.PositiveIntegerField(
        verbose_name="ID чата в Telegram",
        null=True,
        blank=True,
        help_text = "Введите ID чата в Telegram",
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email.split("@")[0]
