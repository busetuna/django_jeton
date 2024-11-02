from django.http import JsonResponse
from django.shortcuts import render
from fuzzywuzzy import fuzz
from uygulama_adi.models import Product as ProductA
from kbkmarket.models import Product2
from django.core.paginator import Paginator
from .models import MatchProduct 


def find_similar_products_and_save(product_list_a, product_list_b, threshold=50):
    matches = []
    for product_a in product_list_a:
        for product_b in product_list_b:
            similarity = fuzz.token_set_ratio(product_a.title, product_b.title)
            if similarity >= threshold:
               
                if not MatchProduct.objects.filter(product_a_id=product_a, product_b_id=product_b).exists():
                    
                    match = MatchProduct(product_a_id=product_a, product_b_id=product_b, similarity=similarity)
                    match.save()
                matches.append((product_a, product_b, similarity))
    return matches


def match_products(request):
    products_a = ProductA.objects.all()
    products_b = Product2.objects.all()


    similar_products = find_similar_products_and_save(products_a, products_b)


    paginator = Paginator(similar_products, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'match/template_name.html', {'page_obj': page_obj})
