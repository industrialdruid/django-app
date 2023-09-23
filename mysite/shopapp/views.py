"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
import logging
from csv import DictWriter

from django.contrib.syndication.views import Feed
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.models import Group, User
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .common import save_csv_products
from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from timeit import default_timer
from .serializers import ProductSerializer, OrderSerializer


log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        # "price",
        # "discount",
        # "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("hello products list")
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount"
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"],
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by ID not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["user", "delivery_address"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user",
        "products",
    ]
    ordering_fields = [
        "delivery_address",
        "created_at",
        "user",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = Product.objects.all()
        context = {
            "time_running": default_timer(),
            "items": 5,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        print("shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


# class ProductCreateView(UserPassesTestMixin, CreateView):
#     def test_func(self):
#         # return self.request.user.groups.filter(name="secret-group").exists()
#         return self.request.user.is_superuser
#     model = Product
#     fields = "name", "price", "description", "discount"
#     success_url = reverse_lazy("shopapp:products_list")


# class ProductCreateView(CreateView):
#     model = Product
#     fields = "name", "price", "description", "discount"
#     success_url = reverse_lazy("shopapp:products_list")
#
#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super().form_valid(form)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = "shopapp.change_product"
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.get_object().created_by

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            #name = form.cleaned_data["name"]
            #price = form.cleaned_data["price"]
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list")
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        "form": form,
    }

    return render(request, "shopapp/create-product.html", context=context)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if not products_data:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({"products": products_data})


class LatestProductsFeed(Feed):
    title = "Latest products"
    description = "New shop products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects
                .filter(created_at__isnull=False)
                .order_by("-created_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]

    def item_price(self, item: Product):
        return item.price


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
            .select_related("user")
            .prefetch_related("products")
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
            .select_related("user")
            .prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products", "promocode", "delivery_address", "preview"
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "user", "products", "promocode", "delivery_address", "preview"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class UserOrdersListView(OrdersListView):
    template_name = 'shopapp/user_orders.html'

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class UserOrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        cache_key = "user_orders_data_export_" + str(user_id)
        orders_data = cache.get(cache_key)
        if not orders_data:
            orders = Order.objects.filter(user=self.owner).order_by("pk").all()
            orders_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "promocode": order.promocode,
                    "user": order.user.pk,
                    "products": [product.pk for product in order.products.all()],
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})




