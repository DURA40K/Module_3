from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db import transaction
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductModelForm


# Статические страницы
class IndexView(TemplateView):
    # Главная страница
    template_name = 'shop/index.html'


class AboutView(TemplateView):
    # Страница 'О нас'
    template_name = 'shop/about.html'


class ContactView(TemplateView):
    # Страница контактов
    template_name = 'shop/contact.html'


# Список товаров
class ProductListView(ListView):
    # Список всех товаров с пагинацией
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 5
    ordering = ['-created_at']


# Детальная страница товара
class ProductDetailView(DetailView):
    # Детальная информация о товаре
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем похожие товары из той же категории (кроме текущего)
        context['similar_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(pk=self.object.pk)[:4]
        return context


# Просмотр заказов пользователя
class MyOrdersView(LoginRequiredMixin, ListView):
    # Просмотр всех заказов текущего пользователя
    model = Order
    template_name = 'shop/my_orders.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Возвращаем только заказы текущего пользователя
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


# CRUD для товаров
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # Создание нового товара
    model = Product
    form_class = ProductModelForm
    template_name = 'shop/add_product.html'
    success_url = reverse_lazy('shop:product_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" успешно добавлен!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление товара'
        return context


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Редактирование товара
    model = Product
    form_class = ProductModelForm
    template_name = 'shop/edit_product.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        return reverse_lazy('shop:product_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Товар "{form.instance.name}" успешно обновлен!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование: {self.object.name}'
        return context


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'shop/product_confirm_delete.html'
    success_url = reverse_lazy('shop:product_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        product_name = self.get_object().name
        messages.success(request, f'Товар "{product_name}" успешно удален!')
        return super().delete(request, *args, **kwargs)


# Аутентификация и регистрация

class CustomLoginView(LoginView):
    # Вход пользователя
    template_name = 'shop/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('shop:product_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    # Выход пользователя
    next_page = reverse_lazy('shop:index')
    http_method_names = ['get', 'post', 'options']
    
    def get(self, request, *args, **kwargs):
        # Обработка GET запроса для logout
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
        return redirect(self.next_page)
    
    def post(self, request, *args, **kwargs):
        # Обработка POST запроса для logout
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
        return redirect(self.next_page)


class RegisterView(CreateView):
    # Регистрация нового пользователя
    form_class = CustomUserCreationForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('shop:product_list')
    
    def form_valid(self, form):
        # Сохраняем пользователя
        user = form.save()
        # Автоматически входим после регистрации
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно!')
        return super().form_valid(form)


# Корзина и оформление заказа

class CartView(LoginRequiredMixin, TemplateView):
    # Просмотр корзины пользователя
    template_name = 'shop/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем или создаем корзину для текущего пользователя
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.all()
        
        # Подсчитываем общую сумму
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        context.update({
            'cart': cart,
            'cart_items': cart_items,
            'total': total,
        })
        return context


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'shop/checkout.html'
    
    def get(self, request, *args, **kwargs):
        # Отображение страницы оформления заказа
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        
        # Если корзина пуста - перенаправляем обратно
        if not cart_items:
            messages.warning(request, 'Ваша корзина пуста!')
            return redirect('shop:cart_view')
        
        # Подсчитываем общую сумму
        total = sum(item.get_total_price() for item in cart_items)
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total': total,
            'user_balance': request.user.balance,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Обработка оформления заказа с использованием транзакции
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        
        # Если корзина пуста - перенаправляем обратно
        if not cart_items:
            messages.warning(request, 'Ваша корзина пуста!')
            return redirect('shop:cart_view')
        
        # Подсчитываем общую сумму
        total = sum(item.get_total_price() for item in cart_items)
        
        # Проверка баланса пользователя
        if request.user.balance < total:
            messages.error(
                request, 
                f'Недостаточно средств на счёте! У вас {request.user.balance} руб., а заказ стоит {total} руб.'
            )
            return redirect('shop:checkout')
        
        try:
            with transaction.atomic():
                # Списываем средства с баланса пользователя
                request.user.balance -= total
                request.user.save()
                
                # Создаем объект Order
                order = Order.objects.create(
                    user=request.user,
                    total_price=total
                )

                # Сохраняем количество и цену на момент покупки
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price_at_order=cart_item.product.price
                    )

                # Очищаем корзину
                cart_items.delete()
                
                # Перенаправляем на страницу с подтверждением
                messages.success(
                    request, 
                    f'Заказ №{order.id} успешно оформлен! Списано {total} руб. Остаток на счете: {request.user.balance} руб.'
                )
                return redirect('shop:my_orders')
                
        except Exception as e:
            # Если произошла ошибка - транзакция откатится автоматически
            messages.error(request, f'Произошла ошибка при оформлении заказа: {str(e)}')
            return redirect('shop:checkout')


class AddToCartView(LoginRequiredMixin, View):
    # Добавление товара в корзину
    
    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            # Если товар уже есть, увеличиваем количество
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Количество "{product.name}" увеличено до {cart_item.quantity}')
        else:
            messages.success(request, f'"{product.name}" добавлен в корзину')
        
        return redirect('shop:cart_view')


class RemoveFromCartView(LoginRequiredMixin, View):
    # Удаление товара из корзины
    
    def get(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.info(request, f'"{product_name}" удален из корзины')
        return redirect('shop:cart_view')


class UpdateCartItemView(LoginRequiredMixin, View):
    # Обновление количества товара в корзине
    
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')
        else:
            cart_item.delete()
            messages.info(request, 'Товар удален из корзины')
        
        return redirect('shop:cart_view')


# Поиск товаров
class SearchProductsView(ListView):
    model = Product
    template_name = 'shop/search_products.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Получение отфильтрованного списка товаров
        search_query = (
            self.request.GET.get('search', '').strip() or 
            self.request.POST.get('search', '').strip()
        )
        
        if search_query:
            # Фильтруем товары по названию
            return Product.objects.filter(name__icontains=search_query)
        
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        # Добавляем поисковый запрос в контекст
        context = super().get_context_data(**kwargs)
        context['search_query'] = (
            self.request.GET.get('search', '').strip() or 
            self.request.POST.get('search', '').strip()
        )
        return context
    
    def post(self, request, *args, **kwargs):
        # Обработка POST запроса 
        return self.get(request, *args, **kwargs)
