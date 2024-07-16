from .models import Productcategory

def menu_list(request):
    links = Productcategory.objects.all()
    return dict(links=links)