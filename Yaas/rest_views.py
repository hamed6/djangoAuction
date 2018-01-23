from Yaas.models import newAuction , bidAuctionModel
from Yaas.serializers import auctionViewSerializer , bidSerializer
from rest_framework.decorators import api_view,renderer_classes, authentication_classes,permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.http import HttpResponse
# from django.contrib import auth
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import datetime
from rest_framework.views import APIView
from django.db.models import Max
from django.http import Http404
import pdb

@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def auctionListApi(request):
    if request.method=='GET':
        auction=newAuction.objects.all().filter(auctionBan=False)
        sz=auctionViewSerializer(auction,many=True)
        return Response(sz.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def auctionSearchApi(request, pk):
    try:
        auction = newAuction.objects.all().filter(auctionBan=False).get(auctionTitle=pk)
    except newAuction.DoesNotExist:
        return HttpResponse(status=404 )

    if request.method=='GET':
        sz=auctionViewSerializer(auction)
        return Response(sz.data)


@api_view(['GET','POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def bidAuctionApi(request , pk):

    try:
        auction=newAuction.objects.get(pk=pk)
    except newAuction.DoesNotExist:
        return Response("Not found",status=404)


    if request.method=='POST':

        # print "=========================================================="

        bidAPI=bidAuctionModel.objects.all().filter(bidAuctionId=pk ,).aggregate(Max('bidPrice'))
        # To find if the auction has any bid or its first time
        if bidAPI['bidPrice__max']==None:
            # bidAPI['bidPrice']=auction.auctionPrice
            price=auction.auctionPrice
        else:
            price=bidAPI['bidPrice__max']

        data=request.data
        serializer=bidSerializer(data=data)

        if serializer.is_valid():

            # To find who is bidding
            if  request.user.username == auction.auctionSeller:
                # pdb.set_trace()
                return Response("Bid on your auction!No way.",status=400)

            # To find bid is lareger than price and also minimus is respected

            elif int(price)+0.01> int(request.data['bidPrice']):
                return Response("Your bid should be > price & previous bids & min increment is 0.01!", status=400)


            # To check whether auction is not banned
            elif auction.auctionBan==True:
                return Response("This auction has been banned by Admin", status=400)


            # To check deadline is not passed
            elif str(auction.auctionDeadline) < str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")):
                return Response("The auction is overdue!", status=400)

            else:
                serializer.save(bidBiddersID=request.user.id,bidAuctionId=pk)
                return Response("Your bid is Saved.",status=200)

        else:
            return Response("Not found2")