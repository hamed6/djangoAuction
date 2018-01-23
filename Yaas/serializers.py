from rest_framework import serializers
from Yaas.models import newAuction , bidAuctionModel

class auctionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model= newAuction
        fields=('id','auctionTitle','auctionDescription','auctionPrice',
                'auctionCreationTime','auctionDeadline','auctionSeller')


class bidSerializer(serializers.ModelSerializer):
    class Meta:
        model= bidAuctionModel
        fields=('bidPrice',)