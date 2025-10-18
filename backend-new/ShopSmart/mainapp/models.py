import string
import random
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from .choices import ShopTypes, ProductTypes,Role
from .managers import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True,null=True,blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, null=True , blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    profile_image = models.URLField(max_length=1024, null=True, blank=True)
    current_address = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_radius_km = models.PositiveIntegerField(default=10)
    onboarding_completed = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='mainapp_user_set',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='mainapp_user_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )
    managed_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_users'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email or self.username


class Shop(models.Model):
    shop_id = models.CharField(max_length=20, unique=True, editable=False)  
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops")
    name = models.CharField(max_length=100)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax percentage for this shop")
    shop_type = models.CharField(max_length=50, choices=ShopTypes.choices)
    
    images = models.JSONField(default=list, help_text="List of image URLs from Firebase Storage")
    
    document_images = models.JSONField(default=list, help_text="List of document image URLs for shop verification")
    
    address = models.TextField()
    location = gis_models.PointField()
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    
    position = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(3)])
    
    # Approval system
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.shop_id:
            self.shop_id = self.generate_shop_id()
        super().save(*args, **kwargs)

    def generate_shop_id(self):
        """Generate unique shop ID with S prefix"""
        while True:
            shop_id = 'S' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Shop.objects.filter(shop_id=shop_id).exists():
                return shop_id

    def __str__(self):
        return f"{self.name} ({self.shop_id})"


class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, editable=False)
    
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50)
    stock_quantity = models.PositiveIntegerField(default=0)

    product_type = models.CharField(max_length=50, choices=ProductTypes.choices)
    
    position = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(3)])

    images = models.JSONField(default=list, help_text="List of image URLs from Firebase Storage")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = self.generate_product_id()
        super().save(*args, **kwargs)

    def generate_product_id(self):
        """Generate unique product ID with P prefix"""
        while True:
            product_id = 'P' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Product.objects.filter(product_id=product_id).exists():
                return product_id

    def __str__(self):
        return f"{self.name} ({self.product_id}) - {self.shop.name}"


class FavoriteShop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_shops")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'shop')

    def __str__(self):
        return f"{self.user} -> {self.shop}"


class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} -> {self.product}"


class ShopReview(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    helpful_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="helpful_shop_reviews", blank=True)

    class Meta:
        unique_together = ('shop', 'user')

    def __str__(self):
        return f"Review for {self.shop.name} by {self.user.username}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    helpful_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="helpful_product_reviews", blank=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"