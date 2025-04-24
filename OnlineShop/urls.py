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

from shop import views
from shop.views import csp_report
from shop.views_scripts.admin_views import upload_view
from shop.views_scripts.profile_orders_pay import create_partial_checkout_session
from shop.router_viewsets import PromoCodeViewSet, StoreViewSet
from shop.views_scripts import profile_views, paypal_views
from shop.views_scripts.adresses_views import update_address, delete_address, create_address
from shop.views_scripts.manage_banners.banners_managing import move_down, move_up, delete_banner_all, \
    delete_banner_relationship, edit_banner
from shop.views_scripts.orders_control.bulk_change_statuses import change_statuses
from shop.views_scripts import catalog_views
from shop.views_scripts.orders_control.download_order import download_csv_order, download_pdf_w_img, \
    download_pdf_no_img, at_delete_order
from shop.views_scripts.orders_control.view_order import view_order, change_in_stock, upload_in_stock, \
    change_tracker_link
from shop.views_scripts.service_views import service_pages_view
from shop.views_scripts.stripe_views import stripe_config, create_checkout_session, CancelledView, SuccessView, \
    stripe_webhook
from shop.views_scripts.users_control.at_uc_bulk_actions import disable_users, enable_users
from shop.views_scripts.auth_views import register, logout_view, login_view, CustomPasswordResetConfirmView, \
    lockout_view
from shop.views_scripts.catalog_views import add_to_cart_from_catalog, catalog_view, change_favorite_state
from shop.views_scripts.checkout_cart_views import sort_documents, send_email, cart_page, anonym_cart_info, \
    register_anonym_cart_info, login_anonym_cart_info, checkout_addresses, checkout_payment_type, check_promo_code
from shop.views_scripts.profile_views import update_user_account, upload_file, generate_product_feed
from shop.views_scripts.shop_views import fetch_numbers, form_page
from shop.views_scripts.users_control.edit_user import edit_user
from shop.views_scripts.users_control.view_user import view_user
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'promocodes', PromoCodeViewSet, basename='promocodes')
router.register(r'stores', StoreViewSet, basename='stores')
urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),

    # Auth urls
    path('login', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register', register, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('lockout/', lockout_view, name='lockout_view'),

    # Product search urls
    path('shop/<str:product_id>', form_page, name='shop_page'),
    path('fetch-numbers/', fetch_numbers, name='fetch_numbers'),

    path('product-feed.<str:fmt>', generate_product_feed, name='product_feed'),

    # Catalog urls
    path('catalog/', catalog_view, name='catalog'),
    path('<str:category_id>-<str:category_name>', catalog_views.param_catalog, name='param_catalog'),

    # Rest api endpoints
    path('api/', include(router.urls)),

    # Checkout urls
    path('cart/', cart_page, name='cart'),
    path('checkout/check-promocode/', check_promo_code, name='check_promocode'),
    path('order/anonymous/info', anonym_cart_info, name='cart_anonymous'),
    path('checkout/addresses', checkout_addresses, name='checkout_addresses'),
    path('anonymous/cart/login', login_anonym_cart_info, name='cart_anonymous_login'),
    path('anonymous/cart/register', register_anonym_cart_info, name='cart_anonymous_register'),
    path('checkout/payment-type/', checkout_payment_type, name='checkout_payment_type'),

    # Addresses urls
    path('profile/addresses/update_address/<str:address_id>/', update_address, name='update_address'),
    path('profile/addresses/delete_address/<str:address_id>/', delete_address, name='delete_address'),
    path('profile/addresses/create_new/', create_address, name='create_address'),

    # Profile urls
    path('profile/<str:feature_name>/', profile_views.profile, name='profile'),
    path('update_user_account/', update_user_account, name='update_user_account'),
    path('upload-file-cart/', upload_file, name='upload_cart'),

    path('delete-document/', views.deleteProduct, name='delete_document'),
    path('update_quantity_input/', views.update_quantity_input, name='update_input'),

    path('sort_documents/', sort_documents, name='sort_documents'),
    path('send-email/', send_email, name='send_email'),

    path('add_to_cart_from_catalog/', add_to_cart_from_catalog, name='add_from_catalog'),
    path('changeFavoriteState/', change_favorite_state, name='change_favorite_state'),
    path('get_cart/', views.getCart, name='get_cart'),

    # Admin tools urls
    path('admin_tools/<str:feature_name>/', views.admin_tools, name='admin_tools'),
    path('at/enable_users/', enable_users, name='at_enable_users'),
    path('at/disable_users/', disable_users, name='at_disable_users'),
    path('at/delete_users/', views.delete_users, name='at_delete_users'),

    path('admin_tools/users_control/edit_user/<str:user_id>/', edit_user, name='at_edit_user'),
    path('admin_tools/users_control/view_user/<str:user_id>/', view_user, name='at_view_user'),
    path('change_statuses/', change_statuses, name='change_few_statuses'),
    path('change_tracker_link/', change_tracker_link, name='change_tracker_link'),
    path('admin_tools/orders_control/view_order/<str:order_id>/', view_order, name='at_view_order'),
    path('admin_tools/orders_control/download_csv/<str:order_id>/', download_csv_order, name='at_download_csv'),
    path('admin_tools/orders_control/download_pdf_no_img/<str:order_id>/', download_pdf_no_img, name='at_download_pdf_no_img'),
    path('admin_tools/orders_control/download_pdf_with_img/<str:order_id>/', download_pdf_w_img, name='at_download_pdf_w_img'),
    path('admin_tools/orders_control/delete_order/<str:order_id>/', at_delete_order, name='at_delete_order'),
    path('admin_tools/orders_control/edit_product_in_stock/', change_in_stock, name='change_in_stock'),
    path('admin_tools/orders_control/upload_in_stock/<str:order_id>/', upload_in_stock, name='upload_in_stock'),
    path('upload-db-update/', upload_view, name='upload_db_update'),

    # Manage banners urls
    path('delete-banner-relationship/<int:rel_id>/', delete_banner_relationship, name='delete_banner_relationship'),
    path('delete-banner-languages/<int:banner_id>/', delete_banner_all, name='delete_banner_all'),
    path('edit-banner/<int:banner_id>/', edit_banner, name='edit_banner'),
    path('move-up/<int:banner_id>/', move_up, name='move_up'),
    path('move-down/<int:banner_id>/', move_down, name='move_down'),

    # Safety urls
    path('csp-report/', csp_report, name='csp_report'),

    # Service urls
    path('content/<str:service_page>', service_pages_view, name='services'),

    # STRIPE
    path('config/', stripe_config, name='stripe_config'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'), # Creating a payment session
    path('success/', SuccessView.as_view(), name='success'),  # Success Page
    path('cancelled/', CancelledView.as_view(), name='cancelled'),  # Cancellation Page
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    # Creating a payment session for partial payment
    path('create-partial-checkout-session/', create_partial_checkout_session, name='create_partial_checkout_session'),

    # PAYPAL
    path('paypal/success/', paypal_views.PayPalSuccessView.as_view(), name='paypal-success'),
    path('paypal/cancelled/', paypal_views.PayPalCancelledView.as_view(), name='paypal-cancelled'),
    path('paypal/create-payment/', paypal_views.create_paypal_payment, name='create-paypal-payment'),
    path('paypal/webhook/', paypal_views.paypal_webhook, name='paypal-webhook'),


)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
