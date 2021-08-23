from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view),
    path('frontier',
         views.stock_create_efficient_frontier_view,
         name='frontier'),
    path('calcualteFrontier',
         views.plot_efficient_frontier,
         name='calcualteFrontier'),
    path('volatility', views.stock_create_volatility_view),
    path('delete_stock/<stock_id>', views.delete_stock, name='delete-stock'),
    # path('calculate_frontier',
    #      views.calculate_frontier,
    #      name='calculate-frontier'),
    # path('add_stock', views.add_stock),
]
