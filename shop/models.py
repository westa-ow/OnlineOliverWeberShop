import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime

from OnlineShop import settings

db = settings.FIRESTORE_CLIENT  # Убедитесь, что Firebase инициализирован
promocodes_ref = db.collection('Promocodes')

# Create your models here.

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="%(app_label)s_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="%(app_label)s_user_set",
        related_query_name="user",
    )
    class Meta:
        app_label = 'shop'


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='imgs/')
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    withLink = models.BooleanField(default=False)
    link = models.CharField(max_length=100, default='')

    class Meta:
        app_label = 'shop'
    def __str__(self):
        return self.title


class PromoCode:
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Скидка в процентах
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)


    @staticmethod
    def get_all():
        # Получение всех документов из коллекции
        docs = promocodes_ref.stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def get_by_id(doc_id):
        # Получение документа по ID
        doc = promocodes_ref.document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def create(data):
        # Преобразуем дату в строку перед сохранением
        doc_id = str(uuid.uuid4())

        # Добавляем creation_date и used_count
        data['id'] = doc_id
        data['creation_date'] = datetime.now()  # Текущая дата/время
        data['used_count'] = 0

        if 'expiration_date' in data and isinstance(data['expiration_date'], date):
            data['expiration_date'] = data['expiration_date'].isoformat()
        promocodes_ref.document(doc_id).set(data)
        return doc_id


    @staticmethod
    def update(doc_id, data):
        # Обновление документа
        promocodes_ref.document(doc_id).update(data)

    @staticmethod
    def delete(doc_id):
        # Удаление документа
        promocodes_ref.document(doc_id).delete()