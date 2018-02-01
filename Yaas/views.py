# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template.backends import django

from Yaas.forms import createAuctionForm ,confirmationForm
from Yaas.models import newAuction, bidAuctionModel , userLanguage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.forms import *
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail, EmailMessage
import urllib, json
from django.db.models import Max
import re
from django.utils.translation import ugettext as _
from django.utils import translation

'''MAIN PAGE'''
def homePage(request):

    checkLanguage(request)

    if request.method == 'POST':
        # call auth_view to see user is registered or not
        auth_view(request)
        if request.user.is_authenticated:
            # output = _(u'Welcome to my site')
            #============================================================
            #to translate the
            # if "lang" in request.session:
            #     translation.activate(request.session["lang"])
            # ============================================================
            checkLanguage(request)
            return render(request, "home.html", {'user': str(request.user.username).title()})
            # return render(request, "home.html", {'user': request.user.username})
        else:
            return render(request, "home.html", {'user': "AnonymousUser"})

    return render(request, "home.html")



'''BROWSE - UC5'''
def browseAuction(request):
    # to find out whether a its admin user or not
    if not request.user.is_staff:
        a_auction = newAuction.objects.all().filter(auctionBan=False )
        if request.method == 'POST':
            try:
                searchTitle = request.POST.get('userTitle')
                uniqueAuction = newAuction.objects.get(auctionTitle=searchTitle, auctionBan=False)
                return render(request, "browseAuction.html", {'uniqueAuctionUser': uniqueAuction})
            except ObjectDoesNotExist:
                messages.error(request, 'Not a valid title')
        return render(request, "browseAuction.html", {'newAuctionHtml': a_auction})

    if request.user.is_staff:
        admin_auc = newAuction.objects.all()
        if request.method == 'POST':
            try:
                searchTitle = request.POST.get('userTitle')
                uniqueAuction = newAuction.objects.get(auctionTitle=searchTitle)
                return render(request, "browseAuction.html", {'uniqueAuctionUser': uniqueAuction})
            except ObjectDoesNotExist:
                messages.error(request, 'Not a valid title')
    return render(request, "browseAuction.html", {'newAuctionHtml': admin_auc})

'''CURRENCY - UC11'''
def currencyChecker(request):
    url = "http://api.fixer.io/latest?base=EUR"
    res = urllib.urlopen(url)
    data = json.loads(res.read())
    a = request.POST.get('t1', ' ')
    if request.method == 'POST' and len(a) == 3:
        url = "http://api.fixer.io/latest?symbols=" + a
        res = urllib.urlopen(url)
        data = json.loads(res.read())
        user = request.POST.get('userCurrency')
        rate = data['rates'][a]
        return render(request, "currency.html", {'msg': float(user) * float(rate), 'userCU': a})
    else:
        return render(request, "currency.html", {'currency': data['rates']})

'''LOGIN'''
def auth_view(request):
    username = request.POST.get('un', '')
    password = request.POST.get('pw', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return messages.success(request, 'Logged in Successfully!')
    else:
        return messages.error(request, 'Logged in Failed!')

'''CREATE USER - UC1'''
def createUser(request):
    if request.method == 'POST':
        form = createAuctionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = createAuctionForm()
    return render(request, "createUser.html", {'form': form})

'''CREATE AUCTION - UC3'''
def createAuction(request):
    if request.user.is_authenticated():
        userDate = request.POST.get('getUserTime')
        op = request.POST.get('Option', '')
        if request.method == 'POST' and len(userDate) > 1 and op == '':
            deadLine = datetime.now() + timedelta(hours=72)
            if datetime.strptime(userDate, '%Y-%m-%dT%H:%M') < deadLine:
                return render(request, "createAuction.html", {'Error': 'At least 3days',
                                                              'postUserTitle': request.POST.get('getUserTitle'),
                                                              'postUserDesc': request.POST.get('getUserDesc'),
                                                              'postUserPrice': request.POST.get('getUserPrice')
                                                              }
                              )
            else:
                return render(request, "createAuction.html", {'postUserTitle': request.POST.get('getUserTitle'),
                                                              'postUserDesc': request.POST.get('getUserDesc'),
                                                              'postUserPrice': request.POST.get('getUserPrice'),
                                                              'postUserTime': request.POST.get('getUserTime'),
                                                              'confirmForm': confirmationForm,
                                                              'confirmLabel': "Are You Sure?"
                                                              }
                              )
        if op == 'Yes':
            saveAuction = newAuction()
            saveAuction.auctionTitle = request.POST.get('getUserTitle')
            saveAuction.auctionDescription = request.POST.get('getUserDesc')
            saveAuction.auctionPrice = request.POST.get('getUserPrice')
            saveAuction.auctionCreationTime = datetime.now()
            saveAuction.auctionDeadline = datetime.strptime(userDate, '%Y-%m-%dT%H:%M')
            saveAuction.auctionSeller = request.user.username
            saveAuction.save()


            mail_subject = "Auction is up!"
            to_email = request.user.email
            email = EmailMessage(mail_subject, "Your Auction is created", to=[to_email])
            email.send()

            return HttpResponseRedirect('/browseAuction/')
        return render(request, "createAuction.html")
    else:
        return HttpResponse('You should have Log in first')

'''LOGOUT'''
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/home/')

''''''
#for user to search and find list of auction/s under his account
def sellerProfile(request):
    myAuction = newAuction.objects.filter(auctionSeller=request.user.username)
    if newAuction.objects.filter(auctionSeller=request.user.username).count() == 0:
        msg = "You don't have auction under YOUR PROFILE"
        return render(request, "sellerProfile.html", {'myAuction': myAuction, 'msg': msg})
    else:
        myAuction = newAuction.objects.filter(auctionSeller=request.user.username)
        return render(request, "sellerProfile.html", {'newAuctionHtml': myAuction})

'''EDIT AUCTION - UC4'''
def editAuction(request, blogID):
    edit = newAuction.objects.get(id=blogID)
    if request.method == 'POST':
        edit.auctionDescription = request.POST.get('getEditedAuction')
        edit.save()
        return HttpResponseRedirect('/sellerProfile/')
    return render(request, "editAuction.html", {'edit': edit})

'''EDIT USER - UC2'''
def editAccount(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            curUser = auth.get_user(request)
            curUser.email = request.POST.get('updateMail')
            curUser.save()
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        return render(request, "editAccount.html", {'form': form})

'''BAN AUCTION - UC7'''
def banAuction(request, pk):
    auction = newAuction.objects.get(pk=pk)
    #ban aution with changing the status
    auction.auctionBan = True
    auction.save()

    # to find the unique mails from all people who bid for a specific auction
    if bidAuctionModel.objects.all().filter(bidAuctionId=pk).count()>0:
        bidAuc=bidAuctionModel.objects.all().filter(bidAuctionId=pk)
        allBidders=bidAuc.values_list('bidBiddersID',flat=True).distinct()
        mail_subject = "Auction Banned!"
        # sending mail to all parties
        for i in allBidders:
            email = EmailMessage(mail_subject, "The auction is banned by Admin.", to=[User.objects.get(id=i).email])
            email.send()
    return HttpResponseRedirect('/browseAuction/')

'''BID - UC6'''
def bidAuction(request, auID):
    auc = newAuction.objects.get(id=auID)

    # to chk user is login
    if request.method == 'POST' and request.user.is_authenticated == False:
        messages.error(request, 'You must be logged in first!')
        return HttpResponseRedirect('/browseAuction/')

        # ==============================================================
        # return HttpResponse(request,"browseAuction.html")
        # return render(request, "browseAuction.html", {'msgBid': "Only register users can bid"})
        # ==============================================================


    # to chk bidder and seller are not same
    if request.method == 'POST' and request.user.username == auc.auctionSeller:
        messages.error(request, 'You cannot bid your own auction!')
        return HttpResponseRedirect('/browseAuction/')

        # ==============================================================
        # return render(request, "browseAuction.html", {'msgBid2': 'You cannot bid your own auction!  Press Search...'})
        # ==============================================================

    if str(auc.auctionDeadline) < str(datetime.now().strftime("%Y-%m-%d %H:%M")):
        messages.error(request, 'The auction is overdue!')
        return HttpResponseRedirect('/browseAuction/')


    # else:
        # try & except for first bid cases
    if request.POST.get('postBid')==None:
        try:
            if bidAuctionModel.objects.all().filter(bidAuctionId=auID).count() >0:
                bidAuc = bidAuctionModel.objects.all().filter(bidAuctionId=auID).aggregate(Max('bidPrice'))
                bidAuc=float( bidAuc['bidPrice__max'])
            else:
                bidau=bidAuctionModel.objects.get(bidAuctionId=auID)
                bidAuc=bidau.bidPrice

            if auc.auctionPrice > bidAuc:
                p = auc.auctionPrice + 0.01
                return render(request, "bidAuction.html", {'aucToBid': auc, 'aucPrice': p , 'origPrice':auc.auctionPrice})
            if auc.auctionPrice < bidAuc:
                return render(request, "bidAuction.html", {'aucToBid': auc, 'aucPrice': bidAuc+ 0.01 ,'origPrice':auc.auctionPrice})
        except ObjectDoesNotExist:
            # for first bidder just add price with 0.01
            return render(request, "bidAuction.html", {'aucToBid': auc, 'aucPrice': auc.auctionPrice + 0.01,
                                                       'origPrice':auc.auctionPrice})
    # to save the bid
    if request.method=='POST':
        '''Concurrency - U10'''
        # to chk concurrency , whether description has changed or not
        if newAuction.objects.get(id=auID).auctionDescription != request.POST.get('aucDesPost'):
            return render(request, "bidAuction.html",{'msg':"Please press back then check again.There is a change!"})
        else:

            bidAuc = bidAuctionModel()

            #finding & sending mail to seller , bidder and previous bidders
            sellerMail = User.objects.get(username=auc.auctionSeller).email
            bidderMail=request.user.email
            bidaucMail = bidAuctionModel.objects.all().filter(bidAuctionId=1)
            prevBidder=bidaucMail.values_list('bidBiddersID',flat=True).distinct()

            mail_subject = "New Bid!"
            email = EmailMessage(mail_subject, "There is a new bid on your item", to=[sellerMail,bidderMail])
            email.send()
            for i in prevBidder:
                email = EmailMessage(mail_subject, "There is a new bid on your item", to=[User.objects.get(id=i).email])
                email.send()

            bidAuc.bidPrice =request.POST.get('bidPrice')
            bidAuc.bidBiddersID = request.user.id
            bidAuc.bidCreateDate =datetime.now()
            bidAuc.bidAuctionId =auc.id
            '''Soft deadline - OP2 '''
            # d=timedelta(minutes=5)
            now= datetime.now(timezone.utc)
            if auc.auctionDeadline -  now == timedelta(minutes=5):
                auc.auctionDeadline+=timedelta(minutes=5)
                newAuction.objects.filter(id=auID).update(auctionDeadline=auc.auctionDeadline)
            bidAuc.save()

            return render(request,"bidAuction.html",{'msg':"Your bid is saved.Press BACK button!",'aucPrice':bidAuc.bidPrice,'origPrice':auc.auctionPrice})
            # bidMSG=messages.info(request, 'Your bid is saved!')
            # return HttpResponseRedirect('/bidAuction/'+auID)




def checkLanguage(request):

    # to check the current status of language, whether it sets or not

    if "lang" in request.session:
      translation.activate(request.session["lang"])

    # to translate based on user click
    if request.GET.get('lang') == 'Pr':

        if request.user.is_authenticated:

            if userLanguage.objects.filter(setUserId=request.user.id).exists() == False:
                instUserLang = userLanguage()
                instUserLang.setUserId = request.user.id
                instUserLang.setUserLang = 'fa'
                instUserLang.save()
            else:
                userLanguage.objects.filter(setUserId=request.user.id).update(setUserLang='fa')

        request.session["lang"] = 'fa'
        translation.activate(request.session["lang"])

    elif request.GET.get('lang') == 'En':

        if request.user.is_authenticated:

            if userLanguage.objects.filter(setUserId=request.user.id).exists() == False:
                instUserLang = userLanguage()
                instUserLang.setUserId = request.user.id
                instUserLang.setUserLang = 'en'
                instUserLang.save()
            else:
                userLanguage.objects.filter(setUserId=request.user.id).update(setUserLang='en')

        request.session["lang"] = 'en'
        translation.activate(request.session["lang"])

    '''Preference Language - OP3'''
    # To find those users with preference
    if request.user.is_authenticated and userLanguage.objects.filter(setUserId=request.user.id).exists():
        request.session["lang"] = getattr(userLanguage.objects.get(setUserId=request.user.id), 'setUserLang')
        translation.activate(request.session["lang"])
