from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Главная страница магазина 
    path('', views.IndexView.as_view(), name='index'),
    
    # Страница "О нас" 
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Страница с контактами 
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Список всех товаров 
    path('products/', views.ProductListView.as_view(), name='product_list'),
    
    # Подробная информация о товаре
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Добавление товара 
    path('products/add/', views.ProductCreateView.as_view(), name='add_product'),
    
    # Редактирование товара 
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='edit_product'),
    
    # Удаление товара 
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='delete_product'),
    
    # Поиск товаров
    path('search/', views.SearchProductsView.as_view(), name='search_products'),
    
    # Корзина
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    
    # Оформление заказа
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Просмотр заказов пользователя
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
    
    # Аутентификация
    path('login/', views.CustomLoginView.as_view(), name='login_view'),
    path('register/', views.RegisterView.as_view(), name='register_view'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout_view'),
]