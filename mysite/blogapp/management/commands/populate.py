import datetime
from django.core.management import BaseCommand
from blogapp.models import Author, Category, Tag, Article
from django.db.models import Q


class Command(BaseCommand):
    def handle(self, *args, **options):
        author_info = {"Tolstoy": "Famous Russian writer",
                       "Huxley": "Famous British/American utopist"}
        categories = ["Story", "Novel"]
        tags = ["Literature", "Utopia", "Epic"]

        self.stdout.write("Populate the database with few examples of blogapp models")

        for name, bio in author_info.items():
            author, created = Author.objects.get_or_create(
                name=name,
                bio=bio,
            )
            author.save()

        for name in categories:
            category, created = Category.objects.get_or_create(name=name)
            category.save()

        for name in tags:
            tag, created = Tag.objects.get_or_create(name=name)
            tag.save()

        article, created = Article.objects.get_or_create(
            title="War and Peace",
            content="Many letters",
            pub_date=datetime.date(1873, 1, 1),
            author=Author.objects.get(name="Tolstoy"),
            category=Category.objects.get(name="Novel")
        )
        article.save()
        article.tags.add(Tag.objects.get(name="Literature"))
        article.tags.add(Tag.objects.get(name="Epic"))

        article, created = Article.objects.get_or_create(
            title="Brave New World",
            content="A bit less letters",
            pub_date=datetime.date(1932, 1, 1),
            author=Author.objects.get(name="Huxley"),
            category=Category.objects.get(name="Novel")
        )
        article.save()
        article.tags.add(Tag.objects.get(name="Literature"))
        article.tags.add(Tag.objects.get(name="Utopia"))

        self.stdout.write("Done")
