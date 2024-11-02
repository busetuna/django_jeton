import time
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.core.paginator import Paginator 
from kbkmarket.models import Product2 
from .models import Product


def scrape_partymarty():
    url = "https://www.partymarty.com.tr/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

       
        product_items = soup.find_all('div', class_='col-6 col-lg-4 col-xl-3')
        
        products_to_save = []  

        for item in product_items:
           
            title_element = item.find('div', class_='showcase-title')
            title = title_element.get_text(strip=True) if title_element else 'Başlık Bulunamadı'

          
            price_element = item.find('div', class_='showcase-price-new')
            price = price_element.span.get_text(strip=True).replace(' TL', '').replace(',', '.').strip() if price_element else '0.0'
            price = float(price) if price else 0.0

           
            product_url_element = item.find('a', class_='showcase-label-container')
            product_url = f"https://www.partymarty.com.tr{product_url_element['href']}" if product_url_element else 'URL Bulunamadı'

          
            image_url = item.find('img')['data-src'] if item.find('img') else ''

           
            if title and product_url:  
                products_to_save.append(Product(title=title, price=price, url=product_url, image_url=image_url))

        return products_to_save 

    else:
        print(f"HTTP request failed: {response.status_code}")
        return []  


def scrape_data(request):
    products_to_save = scrape_partymarty() 

    messages = []

    for product in products_to_save:
      
        existing_product = Product.objects.filter(title=product.title).first() 

        if existing_product:
           
            warning_message = {product.title}
            messages.append(warning_message)
            continue 

        try:
            
            product.save()
            success_message = f"Successfully added product '{product.title}'."
            messages.append(success_message)

        except IntegrityError:
            print(f"Error: Integrity error occurred for product '{product.title}'.")
            error_message = f"Error: Could not save product '{product.title}'."
            messages.append(error_message)

  
    paginator = Paginator(messages, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'uygulama_adi/template_name.html', {'page_obj': page_obj})
