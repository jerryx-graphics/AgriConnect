from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    ProductBatch, SupplyChainEvent, QualityCertificate, BlockchainWallet
)
from products.models import Product

User = get_user_model()


class BlockchainNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainNetwork
        fields = [
            'id', 'name', 'chain_id', 'rpc_url', 'explorer_url',
            'native_currency', 'is_testnet', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SmartContractSerializer(serializers.ModelSerializer):
    network_name = serializers.CharField(source='network.name', read_only=True)

    class Meta:
        model = SmartContract
        fields = [
            'id', 'network', 'network_name', 'contract_type', 'name',
            'address', 'version', 'description', 'is_verified', 'is_active',
            'deployment_tx_hash', 'deployment_block', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'network_name']


class BlockchainTransactionSerializer(serializers.ModelSerializer):
    contract_name = serializers.CharField(source='contract.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'tx_hash', 'block_number', 'transaction_type', 'status',
            'contract', 'contract_name', 'from_address', 'to_address',
            'value', 'gas_used', 'confirmation_count', 'user', 'user_name',
            'product', 'product_name', 'function_name', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'contract_name', 'user_name', 'product_name']


class ProductBatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        fields = [
            'product', 'quantity', 'unit', 'harvest_date', 'expiry_date',
            'farm_location', 'farm_coordinates', 'quality_grade',
            'organic_certified', 'certifications'
        ]

    def create(self, validated_data):
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)


class ProductBatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    blockchain_status = serializers.SerializerMethodField()

    class Meta:
        model = ProductBatch
        fields = [
            'batch_id', 'product', 'product_name', 'farmer', 'farmer_name',
            'quantity', 'unit', 'harvest_date', 'expiry_date', 'farm_location',
            'farm_coordinates', 'quality_grade', 'organic_certified',
            'certifications', 'is_available', 'is_sold', 'remaining_quantity',
            'blockchain_id', 'blockchain_status', 'created_at'
        ]
        read_only_fields = [
            'batch_id', 'farmer', 'farmer_name', 'product_name',
            'blockchain_id', 'blockchain_status', 'created_at'
        ]

    def get_blockchain_status(self, obj):
        if obj.blockchain_tx:
            return {
                'registered': True,
                'tx_hash': obj.blockchain_tx.tx_hash,
                'status': obj.blockchain_tx.status,
                'block_number': obj.blockchain_tx.block_number
            }
        return {'registered': False}


class SupplyChainEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyChainEvent
        fields = [
            'batch', 'event_type', 'timestamp', 'location', 'coordinates',
            'description', 'metadata', 'temperature', 'humidity', 'quality_score'
        ]

    def create(self, validated_data):
        validated_data['actor'] = self.context['request'].user
        return super().create(validated_data)


class SupplyChainEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    blockchain_status = serializers.SerializerMethodField()

    class Meta:
        model = SupplyChainEvent
        fields = [
            'id', 'batch', 'event_type', 'timestamp', 'location', 'coordinates',
            'actor', 'actor_name', 'description', 'metadata', 'is_verified',
            'temperature', 'humidity', 'quality_score', 'blockchain_status',
            'created_at'
        ]
        read_only_fields = ['id', 'actor', 'actor_name', 'is_verified', 'blockchain_status', 'created_at']

    def get_blockchain_status(self, obj):
        if obj.blockchain_tx:
            return {
                'verified': obj.is_verified,
                'tx_hash': obj.blockchain_tx.tx_hash,
                'verification_hash': obj.verification_hash
            }
        return {'verified': False}


class QualityCertificateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityCertificate
        fields = [
            'batch', 'certificate_type', 'issuer', 'certificate_number',
            'issue_date', 'expiry_date', 'certificate_data'
        ]


class QualityCertificateSerializer(serializers.ModelSerializer):
    batch_info = serializers.SerializerMethodField()
    blockchain_status = serializers.SerializerMethodField()

    class Meta:
        model = QualityCertificate
        fields = [
            'certificate_id', 'batch', 'batch_info', 'certificate_type',
            'issuer', 'certificate_number', 'issue_date', 'expiry_date',
            'is_valid', 'certificate_data', 'blockchain_status', 'created_at'
        ]
        read_only_fields = ['certificate_id', 'batch_info', 'blockchain_status', 'created_at']

    def get_batch_info(self, obj):
        return {
            'batch_id': str(obj.batch.batch_id),
            'product_name': obj.batch.product.name,
            'farmer_name': obj.batch.farmer.get_full_name()
        }

    def get_blockchain_status(self, obj):
        if obj.blockchain_tx:
            return {
                'stored': True,
                'tx_hash': obj.blockchain_tx.tx_hash,
                'certificate_hash': obj.certificate_hash,
                'ipfs_hash': obj.ipfs_hash
            }
        return {'stored': False}


class BlockchainWalletSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = BlockchainWallet
        fields = [
            'id', 'user', 'user_name', 'address', 'wallet_type',
            'is_verified', 'last_activity', 'transaction_count',
            'total_gas_used', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'last_activity', 'transaction_count',
            'total_gas_used', 'created_at'
        ]


class WalletVerificationSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=42)
    message = serializers.CharField(max_length=200)
    signature = serializers.CharField(max_length=132)


class BatchVerificationSerializer(serializers.Serializer):
    batch_id = serializers.UUIDField()

    def validate_batch_id(self, value):
        try:
            ProductBatch.objects.get(batch_id=value)
            return value
        except ProductBatch.DoesNotExist:
            raise serializers.ValidationError("Product batch not found")


class SupplyChainJourneySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")