from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BlockchainNetworkViewSet, SmartContractViewSet, BlockchainTransactionViewSet,
    ProductBatchViewSet, SupplyChainEventViewSet, QualityCertificateViewSet,
    BlockchainWalletViewSet, BlockchainAPIViewSet
)

router = DefaultRouter()
router.register(r'networks', BlockchainNetworkViewSet, basename='blockchain-networks')
router.register(r'contracts', SmartContractViewSet, basename='smart-contracts')
router.register(r'transactions', BlockchainTransactionViewSet, basename='blockchain-transactions')
router.register(r'batches', ProductBatchViewSet, basename='product-batches')
router.register(r'events', SupplyChainEventViewSet, basename='supply-chain-events')
router.register(r'certificates', QualityCertificateViewSet, basename='quality-certificates')
router.register(r'wallets', BlockchainWalletViewSet, basename='blockchain-wallets')
router.register(r'api', BlockchainAPIViewSet, basename='blockchain-api')

urlpatterns = [
    path('', include(router.urls)),
]