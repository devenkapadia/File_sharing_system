from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import File, TransferHistory
from .serializers import TransferSerializer, RevokeSerializer, FileSerializer, TransferHistorySerializer
from django.contrib.auth.models import User
from django.db import models
from rest_framework.permissions import IsAuthenticated

class TransferView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/files/
        Returns a list of files owned by the authenticated user or all files if user is staff.
        Optional query param: file_id to get details of a specific file.
        """
        file_id = request.query_params.get('file_id')
        if file_id:
            try:
                file = File.objects.get(id=file_id)
                # Allow access if user is the owner or staff
                if file.owner != request.user and not request.user.is_staff:
                    return Response({'error': 'You do not have permission to view this file'},
                                  status=status.HTTP_403_FORBIDDEN)
                serializer = FileSerializer(file)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except File.DoesNotExist:
                return Response({'error': 'File not found'},
                              status=status.HTTP_404_NOT_FOUND)
        
        # List files: all for staff, owned for regular users
        if request.user.is_staff:
            files = File.objects.all()
        else:
            files = File.objects.filter(owner=request.user)
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        POST /api/transfer/
        Transfers file ownership to another user.
        """
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            file_id = serializer.validated_data['file_id']
            to_user_id = serializer.validated_data['to_user_id']
            
            try:
                file = File.objects.get(id=file_id)
                to_user = User.objects.get(id=to_user_id)
                
                # Check if current user is the owner
                if file.owner != request.user:
                    return Response({'error': 'Only the file owner can transfer'},
                                 status=status.HTTP_403_FORBIDDEN)
                
                # Perform transfer
                TransferHistory.objects.create(
                    file=file,
                    from_user=request.user,
                    to_user=to_user,
                    action='TRANSFER'
                )
                
                # Update file owner
                file.owner = to_user
                file.save()
                
                return Response({
                    'message': 'File transferred successfully',
                    'file': FileSerializer(file).data
                }, status=status.HTTP_200_OK)
                
            except File.DoesNotExist:
                return Response({'error': 'File not found'},
                              status=status.HTTP_404_NOT_FOUND)
            except User.DoesNotExist:
                return Response({'error': 'Target user not found'},
                              status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RevokeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/revoke/
        Returns a list of files the authenticated user can revoke (i.e., they originally transferred and have not revoked).
        """
        # Find files where user was the original transferor and no revoke action exists to them
        transferable_files = File.objects.filter(
            transfer_history__action='TRANSFER',
            transfer_history__from_user=request.user
        ).exclude(
            transfer_history__action='REVOKE',
            transfer_history__to_user=request.user
        ).distinct()
        serializer = FileSerializer(transferable_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        POST /api/revoke/
        Revokes a previous transfer, returning ownership to the original owner.
        """
        serializer = RevokeSerializer(data=request.data)
        if serializer.is_valid():
            file_id = serializer.validated_data['file_id']
            
            try:
                file = File.objects.get(id=file_id)
                
                # Check if user is the original uploader
                first_transfer = file.transfer_history.filter(
                    action='TRANSFER',
                    from_user=request.user
                ).first()
                
                if not first_transfer:
                    return Response({'error': 'Only the original owner can revoke'},
                                 status=status.HTTP_403_FORBIDDEN)
                
                # Perform revocation
                TransferHistory.objects.create(
                    file=file,
                    from_user=file.owner,
                    to_user=request.user,
                    action='REVOKE'
                )
                
                # Update file owner back to original
                file.owner = request.user
                file.save()
                
                return Response({
                    'message': 'File ownership revoked successfully',
                    'file': FileSerializer(file).data
                }, status=status.HTTP_200_OK)
                
            except File.DoesNotExist:
                return Response({'error': 'File not found'},
                              status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/transfer/history/
        Returns transfer history for a specific file or all files for the authenticated user.
        Query param: file_id (optional) to filter by file.
        """
        file_id = request.query_params.get('file_id')
        if file_id:
            try:
                file = File.objects.get(id=file_id)
                # Allow access if user is the owner, was involved in transfer, or is staff
                if (file.owner != request.user and
                    not file.transfer_history.filter(
                        models.Q(from_user=request.user) | models.Q(to_user=request.user)
                    ).exists() and
                    not request.user.is_staff):
                    return Response({'error': 'You do not have permission to view this history'},
                                  status=status.HTTP_403_FORBIDDEN)
                history = file.transfer_history.all()
                serializer = TransferHistorySerializer(history, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except File.DoesNotExist:
                return Response({'error': 'File not found'},
                              status=status.HTTP_404_NOT_FOUND)
        
        # List history for files user owns or was involved in
        history = TransferHistory.objects.filter(
            models.Q(file__owner=request.user) |
            models.Q(from_user=request.user) |
            models.Q(to_user=request.user)
        ).distinct()
        if request.user.is_staff:
            history = TransferHistory.objects.all()
        serializer = TransferHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)