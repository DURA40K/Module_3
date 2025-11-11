from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Product


class CustomUserCreationForm(UserCreationForm):
    # Форма регистрации с кастомной моделью пользователя
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form__input',
            'placeholder': 'email@example.com'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Введите логин'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form__input',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form__input',
            'placeholder': 'Повторите пароль'
        })


class CustomAuthenticationForm(AuthenticationForm):
    # Форма входа
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form__input',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form__input',
            'placeholder': 'Введите пароль'
        })
    )


class ProductModelForm(forms.ModelForm):
    # Форма для создания и редактирования товара
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Введите название товара'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form__input',
                'placeholder': 'Введите описание товара',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form__input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form__input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form__input'
            })
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена (руб.)',
            'category': 'Категория',
            'image': 'Изображение товара'
        }
