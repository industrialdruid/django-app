from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Author(models.Model):
    """
    Модель Author представляет автора статьи. Она имеет два поля:
        name — имя автора. Это поле типа CharField, которое может содержать до 100 символов.
        bio — биография автора. Это поле типа TextField, которое может содержать текстовую информацию произвольной длины.
    """

    name = models.CharField(max_length=100)
    bio = models.TextField(null=False, blank=True)


class Category(models.Model):
    """
    Модель Category представляет категорию статьи. Она имеет одно поле:
        name — название категории. Это поле типа CharField.
    """

    name = models.CharField(max_length=40)


class Tag(models.Model):
    """
    Модель Tag представляет тэг, который можно назначить статье. Она имеет одно поле:
        name — название тэга. Это поле типа CharField.
    """

    name = models.CharField(max_length=20)


class Article(models.Model):
    """
    Модель Article представляет статью. Она имеет следующие поля:
        title — заголовок статьи. Это поле типа CharField. Укажите ограничение по длине. Например, 200 символов.
        content — содержимое статьи. Это поле типа TextField, которое может содержать текстовую информацию произвольной длины.
        pub_date — дата публикации статьи. Это поле типа DateTimeField.
        author — автор статьи. Это поле типа ForeignKey, которое ссылается на модель Author и указывает, что каждая статья принадлежит одному автору.
    Параметр on_delete=models.CASCADE означает, что при удалении автора из базы данных все его статьи также будут удалены.
        category — категория статьи. Это поле типа ForeignKey, которое ссылается на модель Category и указывает, что каждая статья принадлежит одной категории.
    Параметр on_delete=models.CASCADE означает, что при удалении категории из базы данных все статьи в этой категории также будут удалены.
        tags — тэги статьи. Это поле типа ManyToManyField, которое ссылается на модель Tag и позволяет назначать несколько тэгов для каждой статьи.
    При использовании этого поля Django автоматически создаст связующую таблицу в базе данных. Связующая таблица будет содержать записи о том, какие тэги назначены для какой статьи.
    """

    title = models.CharField(max_length=100)
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name="articles")

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})
