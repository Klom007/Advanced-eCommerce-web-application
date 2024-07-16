from django.shortcuts import render, redirect
from .forms import RegistrationForms
from .models import theaccount
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from Orders.models import Order
from .forms import UserForm, UserProfileForm
from .models import UserProfile
from django.shortcuts import get_object_or_404

#send email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from Carts.models import Thecart, cartItem
from Carts.views import _cart_id_session

from Orders.models import OrderProduct


# Create your views here.


def register(request):
    if request.method =='POST':
        form = RegistrationForms(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = theaccount.objects.create_user(first_name=first_name, last_name = last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            #create user profile after registering

            profile = UserProfile()
            profile.user = user
            profile.profile_picture = 'default/default-user.png'
            profile.save()



            #User activation
            current_site = get_current_site(request)
            mail_subject = 'please activate your account'
            message = render_to_string('Accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Email verificatiion link has been sent')
            return redirect('regthank')
    else:
        form = RegistrationForms

    context = {
        'form': form
    }
    return render(request, 'Accounts/register.html', context)


def activate(request, uidb64, token):
    #activating the user by setting the is_active status to true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = theaccount._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, theaccount.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations your account has been activated")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    


def regthank(request):
    return render(request, 'Accounts/regthank.html')




def login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart= Thecart.objects.get(cart_id = _cart_id_session(request)) #assigning the logged in user to the cart item
                is_cart_item_exists = cartItem.objects.filter(thecart=cart).exists()
                if is_cart_item_exists:
                    cart_item = cartItem.objects.filter(thecart = cart)
                    #getting the product variation
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #get the cart items from the user to access his product variation
                    cart_item = cartItem.objects.filter(theuser=user)
         
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existingvariation = item.variations.all()
                        ex_var_list.append(list(existingvariation))
                        id.append(item.id)

                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = cartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.theuser = user
                            item.save()
                        else:
                            cart_item = cartItem.objects.filter(thecart=cart)
                                       
                            for item in cart_item:
                                item.theuser = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request, "Login successful")
            return redirect('store')
        else:
            messages.error(request, 'invalid login credentials')
            return redirect('login')

    return render(request, 'Accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
   auth.logout(request)
   messages.info(request, 'You are logged out')
   
   return redirect('login')



@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user= request.user, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user= request.user)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }

    return render(request, 'Accounts/dashboard.html', context)



def my_orders(request):
     orders = Order.objects.filter(user= request.user, is_ordered=True).order_by('created_at')

     context = {
         'orders': orders,
     }

     return render(request, 'Accounts/my_orders.html', context)




def forgotPassword(request):
    if request.method=='POST':
        theemail = request.POST['email']
        
        if theaccount.objects.filter(email=theemail).exists(): 
            theuser = theaccount.objects.get(email__iexact=theemail) #exact is case sensitive but iexact is case insensitive
            
            #reset passsword reset email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('Accounts/reset_password_email.html',{
                'user': theuser,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(theuser.pk)),
                'token': default_token_generator.make_token(theuser),
            })
            to_email = theemail
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'Accounts/forgotPassword.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = theaccount._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, theaccount.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']= uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired')
        return redirect('login')
    

def resetPassword(request):
    if request.method =='POST':
        thepassword = request.POST['password']
        confirmpass = request.POST['confirm_password']

        if thepassword == confirmpass:
            uid = request.session.get('uid')# in the reset password validate we already got the uid from the session so here we want to retrive the uid. and if you go directly into this resetPassword url it wont work becouse there is no uid in the session
            theuser = theaccount.objects.get(pk=uid)
            theuser.set_password(thepassword) #the db field name is password but for saving password you need the set_password method which would save it in in harsed format
           
            theuser.save()
            messages.success(request, 'Password reset succesful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetPassword')
    else:

        return render(request, 'Accounts/resetPassword.html')
    
@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'Accounts/edit_profile.html', context)






def edit_profile3(request):
    userprofile = get_object_or_404(UserProfile, user = request.user)
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

    if request.method=='POST':
        user_form = UserForm(request.POST, instance = request.user)

        profile_form = UserProfileForm(request.POST, request.FILES, instance= userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your prodile has been updated")
            return redirect('edit_profile')
        else:
            user_form = UserForm(instance=request.user)
            profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,

    }
    return render(request, 'Accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):  #Accessed in the dashboard
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = theaccount.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request) incase you want to log out after changing password
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')

    return render(request, 'Accounts/change_password.html')



def order_detail(request, order_id):

    orderdetail = OrderProduct.objects.filter(order__order_number= order_id)
    order = Order.objects.get(order_number = order_id)

    subtotal = 0 

    for i in orderdetail:
        subtotal += i.product_price * i.quantity

    context = {

        'orderdetail': orderdetail,
        'order': order,
        'subtotal': subtotal, 
    }

    return render(request, 'Accounts/order_detail.html', context)