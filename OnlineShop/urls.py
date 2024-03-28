"""
URL configuration for OnlineShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page,name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),  # You need to create this view
    path('shop/', views.form_page, name='shop_page'),
    path('cart/', views.cart_page, name='cart'),
    path('profile/addresses/update_address/<str:address_id>/', views.update_address, name='update_address'),
    path('profile/addresses/delete_address/<str:address_id>/', views.delete_address, name='delete_address'),
    path('profile/addresses/create_new/', views.create_address, name='create_address'),
    path('profile/<str:feature_name>/', views.profile, name='profile'),
    path('update_user_account/', views.update_user_account, name='update_user_account'),
    path('fetch-numbers/', views.fetch_numbers, name='fetch_numbers'),
    path('add/',views.add_to_cart, name='add_to_cart'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('delete-document/', views.deleteProduct, name='delete_document'),
    path('update_quantity_slider/',views.update_quantity_slider, name='update_slider'),
    path('update_quantity_input/',views.update_quantity_input, name='update_input'),
    path('sort_documents/', views.sort_documents, name='sort_documents'),
    path('send-email/', views.send_email, name='send_email'),
    path('catalog/', views.catalog_view, name='catalog'),

    path('add_to_cart_from_catalog/', views.add_to_cart_from_catalog, name='add_from_catalog'),
    path('get_cart/', views.getCartToBase, name='get_cart'),

    path('admin_tools/<str:feature_name>/', views.admin_tools, name='admin_tools'),
    path('at/enable_users/', views.enable_users, name='at_enable_users'),
    path('at/disable_users/', views.disable_users, name='at_disable_users'),
    path('at/delete_users/', views.delete_users, name='at_delete_users'),
    path('admin_tools/users_control/edit_user/<str:user_id>/', views.edit_user, name='at_edit_user'),
    path('admin_tools/users_control/view_user/<str:user_id>/', views.view_user, name='at_view_user'),

    path('changeFavoriteState/', views.change_favorite_state, name='change_favorite_state')
    # path('finish_order/', )

]
