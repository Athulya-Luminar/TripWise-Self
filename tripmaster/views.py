from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from tripmaster.serializers import UserSerializer, TripSerializer
from django.contrib.auth.models import User
from tripmaster.models import TripDb
from rest_framework import authentication, permissions, serializers
from tripmaster.permissions import OwnerOnly

# Create your views here.

class SignUpView(APIView):
    def post(self, request):
        form_data = request.data
        serializer_instance = UserSerializer(data=form_data)
        
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data={"message": "User created successfully."}, status=201)
        else:
            return Response(data=serializer_instance.errors, status=400)
        


class TripListCreateView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        qs = TripDb.objects.filter(created_by=request.user)
        serializer_instance = TripSerializer(qs, many=True)
        return Response(data=serializer_instance.data, status=200)
    
    def post(self, request):
        form_data = request.data
        serializer_instance = TripSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response(data={"message": "Trip created successfully.",
                                  "trip": serializer_instance.data}, status=201)
        else:
            return Response(data=serializer_instance.errors, status=400)
            
            
class TripRerieveUpdateDeleteView(APIView):
        
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [OwnerOnly]
    
    def get(self, request, pk):
        trip_object = get_object_or_404(TripDb, id=pk)
        # 1, Trip to Munnar, Munnar....2
        if trip_object.created_by == request.user:
            serializer_instance = TripSerializer(trip_object)
            return Response(data=serializer_instance.data, status=200)
        
        else:
            raise serializers.ValidationError("You are not allowed to access this trip.")
        
    def put(self, request, pk):
        trip_object = get_object_or_404(TripDb, id=pk) 
        # 1, Trip to Munnar, Munnar....2
        
        form_data = request.data
        serializer_instance = TripSerializer(data=form_data, instance=trip_object)
        if serializer_instance.is_valid():
            serializer_instance.save() 
            return Response(data={"message": "Trip updated successfully.",
                                  "Updated Trip Details": serializer_instance.data}, status=200)
        else:
            return Response(data=serializer_instance.errors)
            
    def delete(self, request, pk):
        trip_object = get_object_or_404(TripDb, id=pk)
        trip_object.delete()
        return Response(data={"message": "Trip deleted successfully."}, status=200)

    
    
    
    
    
    
    