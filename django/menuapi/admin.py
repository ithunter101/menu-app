from pickle import TRUE
from django.conf import settings
from django.contrib import admin
from menuapi.models import Screen, Category
from django.db import connection
import requests

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    model: Screen
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        r = requests.get('https://publicapi.leaflogix.net/util/AuthorizationHeader/' + settings.APIKEY)
        if r.status_code == 200:
            auth_key = r.json()      
            headers = {
                'authorization': auth_key,
                'consumerkey': settings.APIKEY
            }
            r = requests.get('https://publicapi.leaflogix.net/product-category', headers=headers)
            if r.status_code == 200:
                categories = r.json()
                with connection.cursor() as cursor:
                    for category in categories:  
                        name = category['productCategoryName']
                        id = category['productCategoryId']
                        cursor.execute("UPDATE category SET category_name=%s WHERE id=%s; INSERT INTO category (category_id, category_name, arrangeable, start_on_new) SELECT %s, %s, false, false WHERE NOT EXISTS (SELECT 1 FROM category WHERE category.category_id=%s);", [name, id, id, name, id])
                        # cursor.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = 'category');", [])
                        # (exists,)=cursor.fetchone()
                        # if(exists == TRUE):
                        #     cursor.execute("UPDATE category SET category_name=%s WHERE id=%s; INSERT INTO category (category_id, category_name, arrangeable, start_on_new) SELECT %s, %s, false, false WHERE NOT EXISTS (SELECT 1 FROM category WHERE category.category_id=%s);", [name, id, id, name, id])
                                    