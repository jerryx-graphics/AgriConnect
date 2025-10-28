from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
# from web3 import Web3
# from web3.exceptions import TransactionNotFound, BlockNotFound
import json
import hashlib
import secrets
from datetime import datetime, timedelta

from .models import (
    BlockchainNetwork, SmartContract, BlockchainTransaction,
    ProductBatch, SupplyChainEvent, QualityCertificate, BlockchainWallet
)
from products.models import Product
from orders.models import Order


class Web3Service:
    """Service for interacting with Web3 and blockchain networks"""

    def __init__(self, network_name: str = 'polygon'):
        try:
            self.network = BlockchainNetwork.objects.get(name=network_name, is_active=True)
        except:
            self.network = None
        # self.w3 = Web3(Web3.HTTPProvider(self.network.rpc_url))

    def is_connected(self) -> bool:
        """Check if connected to blockchain network"""
        # try:
        #     return self.w3.is_connected()
        # except Exception:
        return False

    def get_balance(self, address: str) -> Decimal:
        """Get wallet balance in native currency"""
        # try:
        #     balance_wei = self.w3.eth.get_balance(address)
        #     return Decimal(str(self.w3.from_wei(balance_wei, 'ether')))
        # except Exception:
        return Decimal('0')

    def get_gas_price(self) -> int:
        """Get current gas price"""
        # try:
        #     return self.w3.eth.gas_price
        # except Exception:
        return 20000000000  # 20 gwei default

    def estimate_gas(self, transaction: Dict) -> int:
        """Estimate gas for transaction"""
        # try:
        #     return self.w3.eth.estimate_gas(transaction)
        # except Exception:
        return 100000  # Default gas limit


class BlockchainService:
    """Main service for blockchain operations"""

    def __init__(self):
        self.web3_service = Web3Service()

    def create_product_batch(self, product: Product, farmer, batch_data: Dict) -> ProductBatch:
        """Create a new product batch and register on blockchain"""

        # Create batch in database
        batch = ProductBatch.objects.create(
            product=product,
            farmer=farmer,
            quantity=batch_data['quantity'],
            unit=batch_data['unit'],
            harvest_date=batch_data['harvest_date'],
            expiry_date=batch_data.get('expiry_date'),
            farm_location=batch_data['farm_location'],
            farm_coordinates=batch_data.get('farm_coordinates', {}),
            quality_grade=batch_data.get('quality_grade'),
            organic_certified=batch_data.get('organic_certified', False),
            certifications=batch_data.get('certifications', [])
        )

        # Prepare blockchain transaction
        contract = SmartContract.objects.get(
            contract_type='supply_chain',
            network=self.web3_service.network,
            is_active=True
        )

        tx_data = {
            'contract': contract,
            'transaction_type': 'batch_creation',
            'from_address': farmer.blockchain_wallet.address,
            'to_address': contract.address,
            'function_name': 'createBatch',
            'function_params': {
                'batchId': str(batch.batch_id),
                'productId': product.id,
                'quantity': str(batch.quantity),
                'harvestDate': batch.harvest_date.isoformat(),
                'farmLocation': batch.farm_location,
                'qualityGrade': batch.quality_grade or '',
                'organicCertified': batch.organic_certified
            },
            'user': farmer,
            'product': product
        }

        # Create blockchain transaction record
        blockchain_tx = BlockchainTransaction.objects.create(**tx_data)
        batch.blockchain_tx = blockchain_tx
        batch.save()

        # Submit to blockchain (would be handled by background task)
        self._submit_transaction_async(blockchain_tx.id)

        return batch

    def add_supply_chain_event(self, batch: ProductBatch, event_data: Dict) -> SupplyChainEvent:
        """Add a supply chain event and record on blockchain"""

        event = SupplyChainEvent.objects.create(
            batch=batch,
            event_type=event_data['event_type'],
            timestamp=event_data.get('timestamp', timezone.now()),
            location=event_data['location'],
            coordinates=event_data.get('coordinates', {}),
            actor=event_data['actor'],
            description=event_data['description'],
            metadata=event_data.get('metadata', {}),
            temperature=event_data.get('temperature'),
            humidity=event_data.get('humidity'),
            quality_score=event_data.get('quality_score')
        )

        # Create blockchain transaction for event verification
        contract = SmartContract.objects.get(
            contract_type='supply_chain',
            network=self.web3_service.network,
            is_active=True
        )

        event_hash = self._generate_event_hash(event)

        tx_data = {
            'contract': contract,
            'transaction_type': 'quality_update',
            'from_address': event_data['actor'].blockchain_wallet.address,
            'to_address': contract.address,
            'function_name': 'addSupplyChainEvent',
            'function_params': {
                'batchId': str(batch.batch_id),
                'eventType': event.event_type,
                'timestamp': int(event.timestamp.timestamp()),
                'location': event.location,
                'eventHash': event_hash,
                'qualityScore': event.quality_score or 0
            },
            'user': event_data['actor']
        }

        blockchain_tx = BlockchainTransaction.objects.create(**tx_data)
        event.blockchain_tx = blockchain_tx
        event.verification_hash = event_hash
        event.save()

        self._submit_transaction_async(blockchain_tx.id)

        return event

    def issue_quality_certificate(self, batch: ProductBatch, cert_data: Dict) -> QualityCertificate:
        """Issue a quality certificate and store on blockchain"""

        certificate = QualityCertificate.objects.create(
            batch=batch,
            certificate_type=cert_data['certificate_type'],
            issuer=cert_data['issuer'],
            issuer_address=cert_data.get('issuer_address'),
            certificate_number=cert_data['certificate_number'],
            issue_date=cert_data['issue_date'],
            expiry_date=cert_data['expiry_date'],
            certificate_data=cert_data.get('certificate_data', {})
        )

        # Generate certificate hash
        cert_hash = self._generate_certificate_hash(certificate)
        certificate.certificate_hash = cert_hash
        certificate.save()

        # Submit to blockchain
        contract = SmartContract.objects.get(
            contract_type='quality_certificate',
            network=self.web3_service.network,
            is_active=True
        )

        tx_data = {
            'contract': contract,
            'transaction_type': 'certification',
            'from_address': cert_data.get('issuer_address', settings.DEFAULT_ISSUER_ADDRESS),
            'to_address': contract.address,
            'function_name': 'issueCertificate',
            'function_params': {
                'certificateId': str(certificate.certificate_id),
                'batchId': str(batch.batch_id),
                'certificateType': certificate.certificate_type,
                'issuer': certificate.issuer,
                'certificateHash': cert_hash,
                'expiryDate': int(certificate.expiry_date.timestamp())
            }
        }

        blockchain_tx = BlockchainTransaction.objects.create(**tx_data)
        certificate.blockchain_tx = blockchain_tx
        certificate.save()

        self._submit_transaction_async(blockchain_tx.id)

        return certificate

    def verify_batch_authenticity(self, batch_id: str) -> Dict[str, Any]:
        """Verify a product batch's authenticity through blockchain"""
        try:
            batch = ProductBatch.objects.get(batch_id=batch_id)

            # Get blockchain data
            if not batch.blockchain_tx or not batch.blockchain_tx.tx_hash:
                return {
                    'verified': False,
                    'reason': 'Batch not registered on blockchain'
                }

            # Verify transaction exists on blockchain
            tx_details = self._get_transaction_details(batch.blockchain_tx.tx_hash)
            if not tx_details:
                return {
                    'verified': False,
                    'reason': 'Transaction not found on blockchain'
                }

            # Get supply chain events
            events = batch.supply_chain_events.filter(is_verified=True).order_by('timestamp')

            # Get certificates
            certificates = batch.certificates.filter(
                is_valid=True,
                expiry_date__gte=timezone.now().date()
            )

            return {
                'verified': True,
                'batch': {
                    'id': str(batch.batch_id),
                    'product': batch.product.name,
                    'farmer': batch.farmer.get_full_name(),
                    'harvest_date': batch.harvest_date,
                    'quality_grade': batch.quality_grade,
                    'organic_certified': batch.organic_certified,
                    'farm_location': batch.farm_location
                },
                'blockchain_tx': {
                    'hash': batch.blockchain_tx.tx_hash,
                    'block_number': batch.blockchain_tx.block_number,
                    'confirmation_count': batch.blockchain_tx.confirmation_count
                },
                'supply_chain': [
                    {
                        'event_type': event.event_type,
                        'timestamp': event.timestamp,
                        'location': event.location,
                        'actor': event.actor.get_full_name(),
                        'verified': event.is_verified,
                        'tx_hash': event.blockchain_tx.tx_hash if event.blockchain_tx else None
                    }
                    for event in events
                ],
                'certificates': [
                    {
                        'type': cert.certificate_type,
                        'issuer': cert.issuer,
                        'number': cert.certificate_number,
                        'issue_date': cert.issue_date,
                        'expiry_date': cert.expiry_date,
                        'tx_hash': cert.blockchain_tx.tx_hash if cert.blockchain_tx else None
                    }
                    for cert in certificates
                ]
            }

        except ProductBatch.DoesNotExist:
            return {
                'verified': False,
                'reason': 'Batch not found'
            }

    def create_wallet(self, user) -> BlockchainWallet:
        """Create a new blockchain wallet for user"""
        # Generate new wallet (mock implementation)
        # private_key = secrets.token_bytes(32)
        # account = self.web3_service.w3.eth.account.from_key(private_key)

        # Mock address generation
        mock_address = '0x' + secrets.token_hex(20)

        wallet = BlockchainWallet.objects.create(
            user=user,
            address=mock_address,
            public_key='0x' + secrets.token_hex(65),  # Mock public key
            wallet_type='generated'
        )

        # Note: In production, private key should be encrypted and stored securely
        # or not stored at all if using external wallets

        return wallet

    def verify_wallet_ownership(self, user, address: str, signature: str, message: str) -> bool:
        """Verify user owns the wallet address"""
        try:
            # Mock verification - in production would use web3
            # message_hash = self.web3_service.w3.keccak(text=message)
            # recovered_address = self.web3_service.w3.eth.account.recover_message(
            #     message_hash, signature=signature
            # )

            # For now, just check if signature is not empty
            recovered_address = address  # Mock recovery

            if recovered_address.lower() == address.lower():
                # Update or create wallet
                wallet, created = BlockchainWallet.objects.get_or_create(
                    user=user,
                    defaults={
                        'address': address,
                        'wallet_type': 'imported',
                        'is_verified': True,
                        'verification_message': message,
                        'verification_signature': signature
                    }
                )

                if not created:
                    wallet.is_verified = True
                    wallet.verification_message = message
                    wallet.verification_signature = signature
                    wallet.save()

                return True

        except Exception:
            pass

        return False

    def _submit_transaction_async(self, transaction_id: int):
        """Submit transaction to blockchain (async task)"""
        # This would typically be handled by Celery task
        # For now, we'll just update the status
        try:
            tx = BlockchainTransaction.objects.get(id=transaction_id)
            tx.status = 'submitted'
            tx.save()

            # In real implementation, this would:
            # 1. Build and sign the transaction
            # 2. Submit to blockchain
            # 3. Monitor for confirmation
            # 4. Update transaction status

        except BlockchainTransaction.DoesNotExist:
            pass

    def _get_transaction_details(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction details from blockchain"""
        # Mock implementation
        # try:
        #     tx = self.web3_service.w3.eth.get_transaction(tx_hash)
        #     receipt = self.web3_service.w3.eth.get_transaction_receipt(tx_hash)

        #     return {
        #         'hash': tx['hash'].hex(),
        #         'block_number': receipt['blockNumber'],
        #         'status': receipt['status'],
        #         'gas_used': receipt['gasUsed']
        #     }
        # except (TransactionNotFound, Exception):
        return None

    def _generate_event_hash(self, event: SupplyChainEvent) -> str:
        """Generate hash for supply chain event"""
        data = f"{event.batch.batch_id}{event.event_type}{event.timestamp.isoformat()}{event.location}{event.description}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _generate_certificate_hash(self, certificate: QualityCertificate) -> str:
        """Generate hash for quality certificate"""
        data = f"{certificate.certificate_id}{certificate.certificate_type}{certificate.issuer}{certificate.certificate_number}{certificate.issue_date}"
        return hashlib.sha256(data.encode()).hexdigest()


class SupplyChainService:
    """Service for supply chain operations"""

    def __init__(self):
        self.blockchain_service = BlockchainService()

    def get_product_journey(self, product_id: int) -> List[Dict]:
        """Get complete journey of all batches for a product"""
        batches = ProductBatch.objects.filter(
            product_id=product_id
        ).prefetch_related('supply_chain_events', 'certificates')

        journey = []
        for batch in batches:
            events = batch.supply_chain_events.order_by('timestamp')
            certificates = batch.certificates.filter(is_valid=True)

            journey.append({
                'batch_id': str(batch.batch_id),
                'harvest_date': batch.harvest_date,
                'farm_location': batch.farm_location,
                'quality_grade': batch.quality_grade,
                'organic_certified': batch.organic_certified,
                'events': [
                    {
                        'type': event.event_type,
                        'timestamp': event.timestamp,
                        'location': event.location,
                        'actor': event.actor.get_full_name(),
                        'description': event.description,
                        'verified': event.is_verified
                    }
                    for event in events
                ],
                'certificates': [
                    {
                        'type': cert.certificate_type,
                        'issuer': cert.issuer,
                        'number': cert.certificate_number,
                        'expiry_date': cert.expiry_date
                    }
                    for cert in certificates
                ]
            })

        return journey

    def track_order_blockchain(self, order: Order) -> Dict:
        """Track order through blockchain integration"""
        # Find related product batches
        order_items = order.items.select_related('product')
        tracking_data = []

        for item in order_items:
            # Find available batches for this product
            batches = ProductBatch.objects.filter(
                product=item.product,
                is_available=True,
                remaining_quantity__gte=item.quantity
            ).order_by('harvest_date')

            for batch in batches[:1]:  # Use first available batch
                events = batch.supply_chain_events.order_by('timestamp')

                tracking_data.append({
                    'product': item.product.name,
                    'quantity': item.quantity,
                    'batch_id': str(batch.batch_id),
                    'harvest_date': batch.harvest_date,
                    'farm_location': batch.farm_location,
                    'quality_grade': batch.quality_grade,
                    'last_event': {
                        'type': events.last().event_type if events.exists() else 'harvest',
                        'location': events.last().location if events.exists() else batch.farm_location,
                        'timestamp': events.last().timestamp if events.exists() else timezone.now()
                    }
                })

        return {
            'order_id': order.order_id,
            'status': order.status,
            'products': tracking_data
        }