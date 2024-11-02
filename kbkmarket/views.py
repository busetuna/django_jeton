from django.db import IntegrityError
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from .models import Product2
from decimal import Decimal, InvalidOperation

def fetch_product_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('div', class_='ProductName')
        title = title_element.find('h1').find('span').text.strip() if title_element else "Ürün adı bulunamadı"

        price_element = soup.find('span', {'id': 'fiyat'})
        price = None
        if price_element:
            price_text = price_element.find('span', {'class': 'spanFiyat'}).text.strip()
            print(f"Extracted Price Text: {price_text}")  
            price_text = price_text.replace('₺', '').replace('.', '').replace(',', '.').strip()
            try:
                price = Decimal(price_text)
            except (ValueError, InvalidOperation):
                print(f"Fiyat dönüştürme hatası: {price_text}")
        
        if price is None:
            print(f"Price is None for URL: {url}")

        image_element = soup.find('img', {'id': 'imgUrunResim'})
        image_url = image_element['data-original'] if image_element else "Görsel URL bulunamadı"

        return title, price, image_url, url

    except Exception as e:
        print(f"Hata: {str(e)}")
        return None, None, None, url

def scrape_kbkmarket(request):
    base_sitemap_url = "https://www.kbkmarket.com/sitemap/products/{page}.xml"
    messages = []
    product_count = 0
    max_products = 100  # Total product limit
    products_per_page = 10  # Products per page
    current_page = int(request.GET.get('page', 1))  # Get current page from query parameters

    # Calculate the starting page for scraping
    start_page = (current_page - 1) * products_per_page

    for page in range(1, 11):  # Loop through 10 sitemap pages
        if product_count >= max_products:  
            break
        
        sitemap_url = base_sitemap_url.format(page=page)

        try:
            sitemap_response = requests.get(sitemap_url)
            sitemap_response.raise_for_status()
            
            sitemap_soup = BeautifulSoup(sitemap_response.content, 'xml')
            urls = sitemap_soup.find_all('loc')

            for loc in urls:
                if product_count >= max_products:  
                    break
                
                product_url = loc.text
                title, price, image_url, url = fetch_product_data(product_url)

                if title is not None:
                    existing_product = Product2.objects.filter(title__iexact=title.strip()).first()
                    
                    if existing_product:
                        messages.append(f"{title} zaten mevcut.")
                        continue

                    if price is None:
                        messages.append(f"Hata: '{title}' adlı ürün için fiyat bulunamadı. Kaydetme işlemi atlandı.")
                        continue
                    
                    try:
                        Product2.objects.create(
                            title=title.strip(),
                            price=price,
                            url=url,
                            image_url=image_url
                        )
                        messages.append(f"Başarıyla '{title}' adlı ürün eklendi.")
                        product_count += 1

                    except IntegrityError as e:
                        print(f"Hata: Ürün '{title}' için bütünlük hatası oluştu: {e}")
                        messages.append(f"Hata: '{title}' adlı ürün kaydedilemedi.")

        except requests.RequestException as e:
            messages.append(f"Hata: {sitemap_url} yüklenemedi - {str(e)}")
            continue

    # Determine total products in the database for pagination
    total_products = Product2.objects.count()
    total_pages = (total_products // products_per_page) + (1 if total_products % products_per_page > 0 else 0)

    # Generate pagination links
    pagination_links = {
        'current_page': current_page,
        'total_pages': total_pages,
    }

    return render(request, 'kbkmarket/template_name.html', {
        'messages': messages,
        'pagination_links': pagination_links
    })
