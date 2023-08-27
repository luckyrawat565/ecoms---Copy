from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.


class Category(BaseModel):

    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank = True)

    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    
class SubCategory(BaseModel):
    SubCategoryName = models.CharField( max_length=255)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.SubCategoryName
    


class ProductBrand(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)

    def __str__(self):
        return self.name
    

class ColorVariants(BaseModel):
    color_name = models.CharField(max_length=100)    
    details = models.CharField(max_length = 100)
    

    def __str__(self):
        return self.color_name



class Size(BaseModel):
    name = models.CharField(max_length=50)
    details = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Product(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE , related_name='products')
    brand = models.ForeignKey('ProductBrand', on_delete=models.CASCADE, related_name='productsBrand')
    


    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    

class Image(BaseModel):
    product = models.ForeignKey(Product,related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.image}"
    
    

class ProductVariantPrice(BaseModel):    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.price)
    
    

class ProductVariants(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE,related_name = "productVariant")
    vairantName = models.CharField(max_length=50)    
    size = models.ManyToManyField(Size, through='Stock', related_name='variants_size')    
    color = models.ManyToManyField(ColorVariants,through='Stock', related_name='variants_color')    
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.ForeignKey(ProductVariantPrice, on_delete=models.CASCADE, related_name="productPrice",null = True)
  
  
    def save(self,*args, **kwargs):        
        self.slug = slugify(self.vairantName)
        super(ProductVariants, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.product}"
    

class variantImage(BaseModel):
    variant = models.ForeignKey(ProductVariants,related_name='variantimages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')  
        

    def __str__(self):
        return f"{self.image}"
    
class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.user}"
    

    
    
class ProductRating(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.ForeignKey(Review, on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.user}"
    

class Warehouse(BaseModel):
    warehouse_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100) 
    manager_name = models.CharField(max_length=100)

    def __str__(self):
        return self.warehouse_name
    
    

class Stock(BaseModel):
    variant = models.ForeignKey('ProductVariants', on_delete=models.CASCADE,related_name='stock_variants')
    sizes = models.ForeignKey(Size, on_delete=models.CASCADE, default=None)
    colors = models.ForeignKey(ColorVariants, on_delete = models.CASCADE, default=None)        
    stock_quantity = models.PositiveIntegerField()                

    def __str__(self):
        return f"{self.variant.vairantName} - {self.sizes.name} - {self.colors.color_name} - {self.stock_quantity}"
    


class Supplier(BaseModel):
    supplier_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.supplier_name
    




class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)


    def __str__(self):
        return str(self.user)
    
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    stock_variant = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="stock_cart_variant")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"CartItem: {self.variant.product.name} ({self.variant.vairantName})"
    


