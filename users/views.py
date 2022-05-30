import os
import urllib
import uuid
from io import BytesIO
from eth_utils import to_hex, to_wei, to_bytes

from eth_typing import HexStr
from web3 import Web3

import certifi
import requests
from django.conf import settings
from django.contrib.auth import user_logged_in
# Create your views here.
from django.forms import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import BlogMedia
from blog.serializers import BlogMediaSerializer
from users.models import User
from users.serializers import UserSerializer


def saveNewUser(user, avatar_url):
    serializer = UserSerializer(data=user)
    serializer.is_valid(raise_exception=True)
    newUser = serializer.save()

    if avatar_url is not None:
        try:
            file = urllib.request.urlopen(avatar_url, cafile=certifi.where()).read()
            output = BytesIO(file)
            newMedia = BlogMedia(
                media_author=newUser,
                media_status="publish",
                media_parent=None,
                media_category=settings.MEDIA_CATEGORIES["userAvatar"],
                media_file=output
            )
            BlogMedia.full_clean(newMedia)
            BlogMedia.save(newMedia)

        except BaseException as err:
            print(err)

    return newUser


def createCredentials(request, user):
    user_logged_in.send(sender=user.__class__,
                        request=request, user=user)

    refresher = RefreshToken.for_user(user)

    response = Response()
    # response.set_cookie(
    #     key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    #     value=str(refresh.access_token),
    #     max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_MAXAGE'],
    #     secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    #     samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    #     path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
    # )

    response.set_cookie(
        key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
        value=str(refresher),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_MAXAGE'],
        secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH']
    )
    response.data = {"message": "Signed in successfully", "access_token": str(refresher.access_token)}
    response.status_code = status.HTTP_200_OK
    return response


@api_view(['POST'])
@permission_classes([AllowAny, ])
@authentication_classes([])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        try:
            user = User.objects.get(email=email)
            if user:
                if user.check_password(password) is False:
                    return Response({"message": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    res = createCredentials(request, user)
                    return res

                except BaseException as error:
                    print(error)
                    return Response({"message": "User authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "Can not authenticate with the given credentials or the account has been deactivated"},
                    status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"message": "Email or password is wrong"}, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({"message": 'Please provide a email and a password'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyGoogleTokenId(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        payload = {'access_token': request.data["token"]}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)
        if "email" in data:
            user = User.objects.filter(email=data["email"])
            if user.count() == 1:
                try:
                    res = createCredentials(request, user[0])
                    return res
                except BaseException as error:
                    print(f"GG token ID check error: {error}")
                    return Response({"message": "Access token generation failed"}, status=status.HTTP_400_BAD_REQUEST)
            elif user.count() == 0:
                try:
                    avatar_url = None

                    if "picture" in data:
                        avatar_url = data["picture"]

                    userInstance = {
                        "email": data["email"],
                        "full_name": data["name"],
                        "password": str(uuid.uuid4())
                    }
                    newUser = saveNewUser(userInstance, avatar_url)

                    res = createCredentials(request, newUser)
                    res.data["message"] = "Signed in successfully, please change your password in user menu"
                    res.status = status.HTTP_201_CREATED

                    return res
                except BaseException as error:
                    print(error)
                    return Response({"message": "Can not create user with this email, please try again"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "message": "There are more than 1 accounts with this email, please contact admin for more information"},
                    status=status.HTTP_400_BAD_REQUEST)
            # image_url = data["picture"]  # the image on the web
            # save_name = 'my_image.jpg'  # local name to be saved
            # urllib.request.urlretrieve(image_url, f"{settings.MEDIA_ROOT}/{save_name}")

        else:
            return Response({"message": "Google access token authentication failed"},
                            status=status.HTTP_400_BAD_REQUEST)


class UpdateCryptoWalletAddress(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        sender = "0xAA371aa0D70dd1DA713aE3Cd6A6ff7b36ff8dD67"
        receiver = "0xFFf2D0D3C078eE16E86B445D2710227E10bE2d2c"
        tokenAddress = "0x5b4dc6d05b58635dae135109263deb97ecda4978"
        sending_amount = 100
        sender_private_key = "ff6fe2a3a655390155c54bb4b70b103f37474d7152bcbb1c472f8ab09834f2f6"

        contractABI = [
            {
                "constant": True,
                "inputs": [{"name": "recipient", "type": "address"},
                           {"name": "amount", "type": "uint256"}],
                "name": "transfer",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "type": "function",
                "payable": True
            },
            {
                "constant": True,
                "inputs": [
                    {
                        "name": "_owner",
                        "type": "address"
                    }
                ],
                "name": "balanceOf",
                "outputs": [
                    {
                        "name": "balance",
                        "type": "uint256"
                    }
                ],
                "payable": False,
                "type": "function"
            }
        ]
        w3 = Web3(Web3.HTTPProvider('https://rinkeby.infura.io/v3/e24fd90da4f440e8a7400fb923ab8238'))
        contract = w3.eth.contract(address=Web3.toChecksumAddress(tokenAddress),
                                   abi=contractABI)  # declaring the token contract
        token_balance = contract.functions.balanceOf(sender).call()

        amount = to_hex(to_wei(sending_amount, 'ether'))

        data = contract.functions.transfer(Web3.toChecksumAddress(receiver), to_wei(100, 'ether')).buildTransaction({
            "gas": 100000,
            "from": Web3.toChecksumAddress(sender),
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender)
        })

        txObj = {
            "gas": to_hex(100000),
            "to": tokenAddress,
            "value": "0x00",
            "data": data,
            "from": sender,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(sender)
        }

        raw_result = w3.eth.account.signTransaction(data, sender_private_key)
        result = w3.eth.sendRawTransaction(raw_result.rawTransaction)
        print(to_hex(result))
        return Response({"message": "ok"}, status=status.HTTP_200_OK)
