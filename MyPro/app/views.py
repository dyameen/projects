from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class HelloView (APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get (self,request):
        try:
            content = {'message': 'Hello, yameen!'}
            return Response(content)
        except AttributeError:
            pass
