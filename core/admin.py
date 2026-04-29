from django.contrib import admin
from .models import User, Category, Product, Order, OrderItem

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

# Admin Interface Customization (Classic Look)
admin.site.site_header = "Site Administration"
admin.site.site_title = "Site Administration"
admin.site.index_title = "Site Administration"
admin.site.enable_nav_sidebar = False  # Removes the sidebar to restore the classic layout
