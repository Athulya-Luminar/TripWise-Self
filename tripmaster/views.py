from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from tripmaster.serializers import UserSerializer, TripSerializer, TripMemberSerializer
from django.contrib.auth.models import User
from tripmaster.models import TripDb, TripMemberDb
from rest_framework import authentication, permissions, serializers
from tripmaster.permissions import OwnerOnly
from rest_framework.exceptions import PermissionDenied

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



class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer_instance = UserSerializer(users,many=True)
        return Response(data=serializer_instance.data)
        


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

    
    


# API call for Trip Members

class TripMemberListCreateView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, trip_id):
        # Step 1: Get the trip
        trip_object = get_object_or_404(TripDb,id=trip_id)

        # Step 2: Check whether the user is owner or member
        is_owner = trip_object.created_by == request.user
        is_member = TripMemberDb.objects.filter(trip=trip_object,user=request.user).exists()
        if not (is_owner or is_member):
            raise PermissionDenied("You are not allowed to access this trip.")

        # Step 3: Get all members of this trip
        members = TripMemberDb.objects.filter(trip=trip_object)

        # Step 4: Serialize the records
        serializer_instance = TripMemberSerializer(members, many=True)

        return Response(data=serializer_instance.data, status=200)

    def post(self, request, trip_id):

        # Step 1: Get the trip
        trip_object = get_object_or_404(TripDb,id=trip_id)

        # Step 2: Check trip ownership
        if trip_object.created_by != request.user:
            raise PermissionDenied("Only the trip owner can add members.")

        # Step 3: Receive input data
        form_data = request.data

        # Step 4: Create serializer instance
        serializer_instance = TripMemberSerializer(data=form_data,context={'trip': trip_object})

        # Step 5: Validate and save
        if serializer_instance.is_valid():

            serializer_instance.save()
            return Response(
                data={"message": "Trip member added successfully.","member": serializer_instance.data}, status=201)

        else:
            return Response(data=serializer_instance.errors,status=400)


class TripMemberDeleteView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, trip_id, member_id):

        # Step 1: Get the trip
        trip_object = get_object_or_404(TripDb, id=trip_id)

        # Step 2: Check ownership
        if trip_object.created_by != request.user:
            raise PermissionDenied("Only the trip owner can remove members.")

        # Step 3: Get the particular member
        member_object = get_object_or_404(TripMemberDb, id=member_id, trip=trip_object)

        # Step 4: Delete the member
        member_object.delete()

        return Response(
            data={"message": "Trip member removed successfully."},status=200)
    
    



class TripMemberListView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, trip_id):

        # Step 1: Get the trip object
        trip_object = get_object_or_404(TripDb,id=trip_id)

        # Step 2: Check whether the logged-in user is owner or member
        is_owner = trip_object.created_by == request.user

        is_member = TripMemberDb.objects.filter(trip=trip_object, user=request.user).exists()

        if not (is_owner or is_member):
            return Response(data={"message": "You are not allowed to view these members."},status=403)

        # Step 3: Get all members of the particular trip
        members = TripMemberDb.objects.filter(trip=trip_object)

        # Step 4: Serialize the member records
        serializer_instance = TripMemberSerializer(members, many=True)

        # Step 5: Return response
        return Response(data=serializer_instance.data, status=200)
    