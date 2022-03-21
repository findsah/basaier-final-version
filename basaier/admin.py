from django.contrib import admin

# from basaier.models import image_carousel

from .models import  Project , Category , image , demo

# Register your models here.

# @admin.register(signin)
# class signinAdmin(admin.ModelAdmin):
#     list_display = ('id','name','password','phone_number')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=('id','slug','name','nameEn','detail','detailEn','get_category','total_amount','defined_amount','created_by','location','countryFlag','isZakat','isGift','image','image_small','files')
    


admin.site.register(Category)
@admin.register(image)

class imageAdmin(admin.ModelAdmin):
    list_display=('id','title','image')
    
@admin.register(demo)   
class demoAdmin(admin.ModelAdmin):
    list_display=('id','name','email')

    
# @admin.register(signup)
# class signupAdmin(admin.ModelAdmin):
#     list_display = ('id','username','password','email','mobilenumber')
   
