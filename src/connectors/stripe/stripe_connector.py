# File: stripe_connector.py
import os
from typing import Optional, List, Dict, Any
import stripe
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class StripeConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "StripeConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the StripeConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Stripe payment processing integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('STRIPE_API_KEY')
        stripe.api_key = self.api_key

    def connect(self, **kwargs) -> None:
        """Establishes connection with Stripe API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Stripe API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Stripe connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Stripe")
            raise

    def disconnect(self) -> None:
        """Disconnects from Stripe API."""
        try:
            log.info("Disconnecting from Stripe API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Stripe disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Stripe API."""
        try:
            if not self.api_key:
                return False
            stripe_balance = stripe.Balance.retrieve()
            return stripe_balance is not None
        except Exception as e:
            self._handle_exception(e, "Stripe connection validation failed")
            return False

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a customer in Stripe."""
        if not self.connected:
            raise ConnectionError("Not connected to Stripe API")

        try:
            customer = stripe.Customer.create(**customer_data)
            log.info(f"Successfully created customer with ID: {customer.id}")
            return customer
        except Exception as e:
            self._handle_exception(e, "Failed to create customer in Stripe")
            return {}

    def create_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a charge in Stripe."""
        if not self.connected:
            raise ConnectionError("Not connected to Stripe API")

        try:
            charge = stripe.Charge.create(**charge_data)
            log.info(f"Successfully created charge with ID: {charge.id}")
            return charge
        except Exception as e:
            self._handle_exception(e, "Failed to create charge in Stripe")
            return {}

    def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a subscription for a customer in Stripe."""
        if not self.connected:
            raise ConnectionError("Not connected to Stripe API")

        try:
            subscription = stripe.Subscription.create(**subscription_data)
            log.info(f"Successfully created subscription with ID: {subscription.id}")
            return subscription
        except Exception as e:
            self._handle_exception(e, "Failed to create subscription in Stripe")
            return {}

    def refund_charge(self, charge_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Refunds a specific charge in Stripe."""
        if not self.connected:
            raise ConnectionError("Not connected to Stripe API")

        try:
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=amount
            )
            log.info(f"Successfully refunded charge with ID: {charge_id}")
            return refund
        except Exception as e:
            self._handle_exception(e, f"Failed to refund charge with ID: {charge_id}")
            return {}

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['STRIPE_API_KEY']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False