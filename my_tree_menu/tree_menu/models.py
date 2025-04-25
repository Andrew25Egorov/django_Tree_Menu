from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify


class Menu(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name='Название меню'
    )
    slug = models.SlugField(
        max_length=100, unique=True, blank=True, verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Меню'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский пункт',
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название пункта'
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL или named URL'
    )
    named_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Named URL'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order']

    def __str__(self):
        return f'{self.title} ({self.menu.name})'

    def get_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.url or '#'
        return self.url or '#'
