from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import BaseModel
from products.models import Product
from orders.models import Order

User = get_user_model()


class BlockchainNetwork(BaseModel):
    """Represents different blockchain networks"""
    NETWORK_CHOICES = [
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('bsc', 'Binance Smart Chain'),
        ('avalanche', 'Avalanche'),
        ('arbitrum', 'Arbitrum'),
    ]

    name = models.CharField(max_length=50, choices=NETWORK_CHOICES, unique=True)
    chain_id = models.PositiveIntegerField(unique=True)
    rpc_url = models.URLField()
    explorer_url = models.URLField()
    native_currency = models.CharField(max_length=10, default='ETH')
    is_testnet = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'Testnet' if self.is_testnet else 'Mainnet'})"


class SmartContract(BaseModel):
    """Smart contract deployments on different networks"""
    CONTRACT_TYPE_CHOICES = [
        ('supply_chain', 'Supply Chain Tracking'),
        ('payment_escrow', 'Payment Escrow'),
        ('quality_certificate', 'Quality Certificate'),
        ('farmer_registry', 'Farmer Registry'),
        ('marketplace', 'Marketplace'),
    ]

    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42, help_text="Contract address on blockchain")
    abi = models.JSONField(help_text="Contract ABI (Application Binary Interface)")
    bytecode = models.TextField(null=True, blank=True, help_text="Contract bytecode")

    # Deployment info
    deployment_tx_hash = models.CharField(max_length=66, null=True, blank=True)
    deployment_block = models.PositiveIntegerField(null=True, blank=True)
    deployer_address = models.CharField(max_length=42, null=True, blank=True)

    # Contract metadata
    version = models.CharField(max_length=20, default='1.0.0')
    description = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['network', 'contract_type', 'version']

    def __str__(self):
        return f"{self.name} on {self.network.name}"


class BlockchainTransaction(BaseModel):
    """Tracks blockchain transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('product_registration', 'Product Registration'),
        ('ownership_transfer', 'Ownership Transfer'),
        ('quality_update', 'Quality Update'),
        ('payment_escrow', 'Payment Escrow'),
        ('payment_release', 'Payment Release'),
        ('certification', 'Certification'),
        ('batch_creation', 'Batch Creation'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('reverted', 'Reverted'),
    ]

    # Transaction identifiers
    tx_hash = models.CharField(max_length=66, unique=True, null=True, blank=True)
    block_number = models.PositiveIntegerField(null=True, blank=True)
    block_hash = models.CharField(max_length=66, null=True, blank=True)
    transaction_index = models.PositiveIntegerField(null=True, blank=True)

    # Transaction details
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    value = models.DecimalField(max_digits=30, decimal_places=18, default=Decimal('0'))
    gas_price = models.DecimalField(max_digits=30, decimal_places=18, null=True, blank=True)
    gas_used = models.PositiveIntegerField(null=True, blank=True)
    gas_limit = models.PositiveIntegerField(null=True, blank=True)

    # Status and timing
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    nonce = models.PositiveIntegerField(null=True, blank=True)
    confirmation_count = models.PositiveIntegerField(default=0)

    # Related data
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockchain_transactions', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='blockchain_transactions', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='blockchain_transactions', null=True, blank=True)

    # Transaction data
    input_data = models.TextField(null=True, blank=True)
    function_name = models.CharField(max_length=100, null=True, blank=True)
    function_params = models.JSONField(default=dict)

    # Error handling
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tx_hash']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'transaction_type']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.tx_hash or 'Pending'}"


class ProductBatch(BaseModel):
    """Blockchain-tracked product batches for supply chain transparency"""
    batch_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produced_batches')

    # Batch details
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit = models.CharField(max_length=20, choices=[
        ('kg', 'Kilogram'),
        ('ton', 'Ton'),
        ('piece', 'Piece'),
        ('bag', 'Bag'),
        ('crate', 'Crate'),
    ])

    # Location and timing
    harvest_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    farm_location = models.CharField(max_length=200)
    farm_coordinates = models.JSONField(default=dict, help_text="Latitude and longitude")

    # Blockchain data
    blockchain_tx = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_batches')
    blockchain_id = models.CharField(max_length=100, null=True, blank=True, help_text="Unique ID on blockchain")
    merkle_root = models.CharField(max_length=66, null=True, blank=True, help_text="Merkle root for batch verification")

    # Quality and certification
    quality_grade = models.CharField(max_length=2, choices=[
        ('A+', 'Premium Grade'),
        ('A', 'Grade A'),
        ('B', 'Grade B'),
        ('C', 'Grade C'),
    ], null=True, blank=True)

    organic_certified = models.BooleanField(default=False)
    certifications = models.JSONField(default=list, help_text="List of certifications")

    # Status tracking
    is_available = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)
    remaining_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-harvest_date']

    def __str__(self):
        return f"Batch {self.batch_id} - {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.remaining_quantity:
            self.remaining_quantity = self.quantity
        super().save(*args, **kwargs)


class SupplyChainEvent(BaseModel):
    """Track events in the supply chain on blockchain"""
    EVENT_TYPE_CHOICES = [
        ('harvest', 'Harvest'),
        ('processing', 'Processing'),
        ('packaging', 'Packaging'),
        ('quality_check', 'Quality Check'),
        ('storage', 'Storage'),
        ('transport_start', 'Transport Started'),
        ('transport_end', 'Transport Completed'),
        ('delivery', 'Delivery'),
        ('sale', 'Sale'),
    ]

    batch = models.ForeignKey(ProductBatch, on_delete=models.CASCADE, related_name='supply_chain_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=200)
    coordinates = models.JSONField(default=dict, null=True, blank=True)

    # Event details
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supply_chain_events')
    description = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Additional event data")

    # Blockchain verification
    blockchain_tx = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_hash = models.CharField(max_length=66, null=True, blank=True)

    # Quality data
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quality_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(100)])

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.batch.batch_id} at {self.timestamp}"


class QualityCertificate(BaseModel):
    """Digital quality certificates stored on blockchain"""
    CERTIFICATE_TYPE_CHOICES = [
        ('organic', 'Organic Certification'),
        ('fair_trade', 'Fair Trade'),
        ('global_gap', 'GlobalGAP'),
        ('haccp', 'HACCP'),
        ('iso_22000', 'ISO 22000'),
        ('kenya_organic', 'Kenya Organic'),
        ('custom', 'Custom Certification'),
    ]

    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    batch = models.ForeignKey(ProductBatch, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES)

    # Certificate details
    issuer = models.CharField(max_length=200, help_text="Certifying organization")
    issuer_address = models.CharField(max_length=42, null=True, blank=True, help_text="Blockchain address of issuer")
    certificate_number = models.CharField(max_length=100, unique=True)

    # Validity
    issue_date = models.DateField()
    expiry_date = models.DateField()
    is_valid = models.BooleanField(default=True)

    # Blockchain storage
    blockchain_tx = models.ForeignKey(BlockchainTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    ipfs_hash = models.CharField(max_length=100, null=True, blank=True, help_text="IPFS hash for certificate document")
    certificate_hash = models.CharField(max_length=66, help_text="Hash of certificate for verification")

    # Certificate content
    certificate_data = models.JSONField(default=dict, help_text="Certificate details and standards met")

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.certificate_type} - {self.certificate_number}"


class BlockchainWallet(BaseModel):
    """User blockchain wallets for AgriConnect"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blockchain_wallet')

    # Wallet details
    address = models.CharField(max_length=42, unique=True)
    public_key = models.CharField(max_length=130, null=True, blank=True)

    # Wallet metadata
    wallet_type = models.CharField(max_length=20, choices=[
        ('metamask', 'MetaMask'),
        ('walletconnect', 'WalletConnect'),
        ('generated', 'Platform Generated'),
        ('imported', 'Imported'),
    ], default='generated')

    # Security
    is_verified = models.BooleanField(default=False)
    verification_message = models.CharField(max_length=200, null=True, blank=True)
    verification_signature = models.CharField(max_length=132, null=True, blank=True)

    # Activity tracking
    last_activity = models.DateTimeField(null=True, blank=True)
    transaction_count = models.PositiveIntegerField(default=0)
    total_gas_used = models.DecimalField(max_digits=30, decimal_places=18, default=Decimal('0'))

    class Meta:
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['user', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.address[:10]}..."
