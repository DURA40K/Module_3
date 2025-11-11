from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem, Purchase

# Кастомная админка для пользователей
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'date_joined')
    
    # Поля для поиска
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    # Фильтры в боковой панели
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    # Добавляем наши кастомные поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'date_of_birth', 'avatar')
        }),
    )
    
    # Поля для формы добавления нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'phone', 'date_of_birth', 'avatar')
        }),
    )

# Админка для категорий
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

# Админка для товаров
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price',)  # Можно редактировать цену прямо в списке

# Inline для товаров в корзине
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # Не показывать пустые строки
    readonly_fields = ('added_at',)

# Админка для корзины
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'get_items_count')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Товаров в корзине'

# Админка для товаров корзины
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('added_at', 'product__category')
    readonly_fields = ('added_at',)

# Inline для товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

# Админка для заказов
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'updated_at', 'get_items_count')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Товаров в заказе'

# Админка для товаров заказа
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_order', 'created_at')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('created_at', 'updated_at', 'product__category')
    readonly_fields = ('created_at', 'updated_at')

# Админка для покупок
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'total_price', 'paid_at')
    search_fields = ('order_item__order__user__username', 'order_item__product__name')
    list_filter = ('paid_at',)
    readonly_fields = ('paid_at',)

# Регистрируем все модели в админке
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Purchase, PurchaseAdmin)
