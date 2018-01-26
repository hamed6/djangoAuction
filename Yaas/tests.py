# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from django.test import TestCase
from Yaas.models import newAuction , bidAuctionModel
from autofixture import AutoFixture
# Create your tests here.



class auctionTest(TestCase):
    def test_initialTest(self):
        self.failUnlessEqual(1+1,2)


