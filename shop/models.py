import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime

from OnlineShop import settings

db = settings.FIRESTORE_CLIENT
promocodes_ref = db.collection('Promocodes')


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


class Language(models.Model):
    code = models.CharField(max_length=2, unique=True)  # 'gb', 'it', 'es', 'de', 'ru', 'fr'
    name = models.CharField(max_length=50) # 'English', 'Italian', 'Spanish', 'German', 'Russian', 'French'

    def __str__(self):
        return self.name


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='imgs/')
    active = models.BooleanField(default=True)
    withLink = models.BooleanField(default=False)
    link = models.CharField(max_length=100, default='')
    # BannerLanguage - model that connects Banner and Language
    languages = models.ManyToManyField(Language, through='BannerLanguage')

    class Meta:
        app_label = 'shop'

    def __str__(self):
        return self.title


class BannerLanguage(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name='banner_languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)

    class Meta:
        unique_together = ('banner', 'language')
        ordering = ['priority']

    def __str__(self):
        return f"{self.banner.title} – {self.language.code} (Priority: {self.priority})"


class PromoCode:
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage discount
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)


    @staticmethod
    def get_all():
        # Retrieving all documents in the collection
        docs = promocodes_ref.stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def get_by_id(doc_id):
        # Retrieving a document by ID
        doc = promocodes_ref.document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def create(data):
        # Convert the date to a string before saving it
        doc_id = str(uuid.uuid4())

        # Add creation_date and used_count
        data['id'] = doc_id
        data['creation_date'] = datetime.now()  # Current date/time
        data['used_count'] = 0

        if 'expiration_date' in data and isinstance(data['expiration_date'], date):
            data['expiration_date'] = data['expiration_date'].isoformat()
        promocodes_ref.document(doc_id).set(data)
        return doc_id


    @staticmethod
    def update(doc_id, data):
        # Updating a document
        promocodes_ref.document(doc_id).update(data)

    @staticmethod
    def delete(doc_id):
        # Deleting a document
        promocodes_ref.document(doc_id).delete()


class Store(models.Model):
    address = models.CharField(max_length=255, verbose_name='Address')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Latitude')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Logitude')

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.address
