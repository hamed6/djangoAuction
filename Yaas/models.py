#-*- coding: utf-8 -*-

# from __future__ import unicode_literals
from django.db import models
#from datetime import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.
class newAuction(models.Model):
    auctionTitle=models.CharField(max_length=30)
    auctionDescription=models.CharField(max_length=50)
    auctionPrice=models.PositiveIntegerField(default=0)
    auctionCreationTime = models.DateTimeField()
    auctionDeadline=models.DateTimeField()
    auctionSeller=models.CharField(max_length=30)
    auctionBan=models.BooleanField(default=False)
    auctionResolved=models.BooleanField(default=False)


    def __str__(self):
        return self.auctionTitle


class bidAuctionModel(models.Model):
    bidPrice=models.DecimalField(max_digits=6, decimal_places=2)
    bidBiddersID=models.PositiveIntegerField(default=0)
    bidCreateDate=models.DateTimeField(auto_now_add=True)
    bidAuctionId=models.IntegerField(default=0)

    def __str__(self):
        return self.bidBiddersID

class userLanguage(models.Model):
    setUserLang = models.CharField(max_length=3, default='en')
    setUserId = models.PositiveIntegerField()