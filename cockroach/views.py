from instagram.models import InstagramList
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
#                                    HTTP_404_NOT_FOUND)
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from cockroach.serializers import UserSerializer, GroupSerializer


def index(request):
    # current_user = request.user
    instagrams = InstagramList.objects.filter(actived=True)
    # return render(request, 'index.html', {'pd': postdata, 'pdcount': pdcount, 'user': current_user, 'fanpages': fanpages})
    return render(request, 'cockroach/index.html', {'instagrams': instagrams})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
