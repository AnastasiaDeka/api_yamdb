"""Команда для импорта данных из CSV файлов в базу данных."""
import csv
from django.core.management.base import BaseCommand
from reviews.models import User, Title, Category, Genre, Review, Comment


class Command(BaseCommand):
    """Импортирует данные из CSV файлов в базы данных для моделей."""

    help = 'Parse data from CSV files and insert into the database'

    def handle(self, *args, **kwargs):
        """Обрабатывает CSV файлы, добавляет данные в модели."""
        csv_files = [
            'users.csv',
            'category.csv',
            'genre.csv',
            'titles.csv',
            'genre_title.csv',
            'review.csv',
            'comments.csv',
        ]

        for file in csv_files:
            with open(f'static/data/{file}', newline='',
                      encoding='utf-8') as csvfile:
                data = csv.reader(csvfile)
                next(data)  # Skip the header row
                for row in data:
                    if file == 'users.csv':
                        User.objects.create(
                            id=int(row[0]),
                            username=row[1],
                            email=row[2],
                            role=row[3],
                            bio=row[4],
                            first_name=row[5],
                            last_name=row[6]
                        )
                    elif file == 'titles.csv':
                        Title.objects.create(
                            id=int(row[0]),
                            name=row[1],
                            year=int(row[2]),
                            category_id=int(row[3])
                        )
                    elif file == 'category.csv':
                        Category.objects.create(
                            id=int(row[0]),
                            name=row[1],
                            slug=row[2]
                        )
                    elif file == 'genre.csv':
                        Genre.objects.create(
                            id=int(row[0]),
                            name=row[1],
                            slug=row[2]
                        )
                    elif file == 'review.csv':
                        Review.objects.create(
                            id=int(row[0]),
                            title_id=int(row[1]),
                            text=row[2],
                            author_id=int(row[3]),
                            score=int(row[4]),
                            pub_date=row[5]
                        )
                    elif file == 'comments.csv':
                        Comment.objects.create(
                            id=int(row[0]),
                            review_id=int(row[1]),
                            text=row[2],
                            author_id=int(row[3]),
                            pub_date=row[4]
                        )
                    elif file == 'genre_title.csv':
                        title = Title.objects.get(id=int(row[1]))
                        genre = Genre.objects.get(id=int(row[2]))
                        title.genre.add(genre)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
