from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from core.permissions import IsOwnerOrReadOnly, IsFarmerOrReadOnly
from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    ProductBatch, SupplyChainEvent, QualityCertificate, BlockchainWallet
)
from .serializers import (
    BlockchainNetworkSerializer, SmartContractSerializer, BlockchainTransactionSerializer,
    ProductBatchSerializer, ProductBatchCreateSerializer, SupplyChainEventSerializer,
    SupplyChainEventCreateSerializer, QualityCertificateSerializer,
    QualityCertificateCreateSerializer, BlockchainWalletSerializer,
    WalletVerificationSerializer, BatchVerificationSerializer, SupplyChainJourneySerializer
)
from .services import BlockchainService, SupplyChainService


class BlockchainNetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain networks"""
    queryset = BlockchainNetwork.objects.filter(is_active=True)
    serializer_class = BlockchainNetworkSerializer
    permission_classes = [IsAuthenticated]


class SmartContractViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for smart contracts"""
    queryset = SmartContract.objects.filter(is_active=True)
    serializer_class = SmartContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['network', 'contract_type', 'is_verified']


class BlockchainTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain transactions"""
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'transaction_type', 'user', 'product']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return BlockchainTransaction.objects.all()
        return BlockchainTransaction.objects.filter(
            Q(user=user) | Q(product__farmer=user)
        )


class ProductBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for product batches"""
    permission_classes = [IsAuthenticated, IsFarmerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'farmer', 'quality_grade', 'organic_certified', 'is_available']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return ProductBatch.objects.all()
        elif user.role == 'FARMER':
            return ProductBatch.objects.filter(farmer=user)
        else:
            return ProductBatch.objects.filter(is_available=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductBatchCreateSerializer
        return ProductBatchSerializer

    def perform_create(self, serializer):
        batch = serializer.save()

        # Register batch on blockchain
        blockchain_service = BlockchainService()
        try:
            blockchain_service.create_product_batch(
                batch.product,
                self.request.user,
                {
                    'quantity': batch.quantity,
                    'unit': batch.unit,
                    'harvest_date': batch.harvest_date,
                    'expiry_date': batch.expiry_date,
                    'farm_location': batch.farm_location,
                    'farm_coordinates': batch.farm_coordinates,
                    'quality_grade': batch.quality_grade,
                    'organic_certified': batch.organic_certified,
                    'certifications': batch.certifications
                }
            )
        except Exception as e:
            # Log error but don't fail the creation
            pass

    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify batch authenticity through blockchain"""
        batch = self.get_object()
        blockchain_service = BlockchainService()

        verification_result = blockchain_service.verify_batch_authenticity(str(batch.batch_id))

        return Response(verification_result)

    @action(detail=True, methods=['get'])
    def supply_chain(self, request, pk=None):
        """Get supply chain journey for batch"""
        batch = self.get_object()
        supply_chain_service = SupplyChainService()

        journey = supply_chain_service.get_product_journey(batch.product.id)

        # Filter for this specific batch
        batch_journey = [j for j in journey if j['batch_id'] == str(batch.batch_id)]

        return Response({
            'batch_id': str(batch.batch_id),
            'journey': batch_journey
        })


class SupplyChainEventViewSet(viewsets.ModelViewSet):
    """ViewSet for supply chain events"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['batch', 'event_type', 'actor', 'is_verified']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return SupplyChainEvent.objects.all()
        return SupplyChainEvent.objects.filter(
            Q(actor=user) | Q(batch__farmer=user)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return SupplyChainEventCreateSerializer
        return SupplyChainEventSerializer

    def perform_create(self, serializer):
        event = serializer.save()

        # Add event to blockchain
        blockchain_service = BlockchainService()
        try:
            blockchain_service.add_supply_chain_event(
                event.batch,
                {
                    'event_type': event.event_type,
                    'timestamp': event.timestamp,
                    'location': event.location,
                    'coordinates': event.coordinates,
                    'actor': event.actor,
                    'description': event.description,
                    'metadata': event.metadata,
                    'temperature': event.temperature,
                    'humidity': event.humidity,
                    'quality_score': event.quality_score
                }
            )
        except Exception as e:
            # Log error but don't fail the creation
            pass


class QualityCertificateViewSet(viewsets.ModelViewSet):
    """ViewSet for quality certificates"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['batch', 'certificate_type', 'issuer', 'is_valid']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'COOPERATIVE']:
            return QualityCertificate.objects.all()
        return QualityCertificate.objects.filter(batch__farmer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return QualityCertificateCreateSerializer
        return QualityCertificateSerializer

    def perform_create(self, serializer):
        certificate = serializer.save()

        # Store certificate on blockchain
        blockchain_service = BlockchainService()
        try:
            blockchain_service.issue_quality_certificate(
                certificate.batch,
                {
                    'certificate_type': certificate.certificate_type,
                    'issuer': certificate.issuer,
                    'certificate_number': certificate.certificate_number,
                    'issue_date': certificate.issue_date,
                    'expiry_date': certificate.expiry_date,
                    'certificate_data': certificate.certificate_data
                }
            )
        except Exception as e:
            # Log error but don't fail the creation
            pass


class BlockchainWalletViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain wallets"""
    serializer_class = BlockchainWalletSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return BlockchainWallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_wallet(self, request):
        """Create a new blockchain wallet for user"""
        if hasattr(request.user, 'blockchain_wallet'):
            return Response(
                {'error': 'User already has a wallet'},
                status=status.HTTP_400_BAD_REQUEST
            )

        blockchain_service = BlockchainService()
        wallet = blockchain_service.create_wallet(request.user)

        serializer = self.get_serializer(wallet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify_wallet(self, request):
        """Verify wallet ownership"""
        serializer = WalletVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blockchain_service = BlockchainService()
        verified = blockchain_service.verify_wallet_ownership(
            request.user,
            serializer.validated_data['address'],
            serializer.validated_data['signature'],
            serializer.validated_data['message']
        )

        if verified:
            wallet = BlockchainWallet.objects.get(user=request.user)
            wallet_serializer = self.get_serializer(wallet)
            return Response({
                'verified': True,
                'wallet': wallet_serializer.data
            })
        else:
            return Response(
                {'verified': False, 'error': 'Wallet verification failed'},
                status=status.HTTP_400_BAD_REQUEST
            )


class BlockchainAPIViewSet(viewsets.ViewSet):
    """General blockchain API endpoints"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def verify_batch(self, request):
        """Verify product batch authenticity"""
        serializer = BatchVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blockchain_service = BlockchainService()
        verification_result = blockchain_service.verify_batch_authenticity(
            str(serializer.validated_data['batch_id'])
        )

        return Response(verification_result)

    @action(detail=False, methods=['post'])
    def product_journey(self, request):
        """Get complete supply chain journey for a product"""
        serializer = SupplyChainJourneySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        supply_chain_service = SupplyChainService()
        journey = supply_chain_service.get_product_journey(
            serializer.validated_data['product_id']
        )

        return Response({
            'product_id': serializer.validated_data['product_id'],
            'batches': journey
        })

    @action(detail=False, methods=['get'])
    def network_status(self, request):
        """Get blockchain network status"""
        blockchain_service = BlockchainService()

        return Response({
            'connected': blockchain_service.web3_service.is_connected(),
            'network': blockchain_service.web3_service.network.name,
            'chain_id': blockchain_service.web3_service.network.chain_id,
            'is_testnet': blockchain_service.web3_service.network.is_testnet
        })
