from abc import ABC, abstractmethod


class IPaymentProvider(ABC):
    @abstractmethod
    def verify_transaction(self, transaction_id: str) -> dict:
        """
        Verify a transaction with the external payment gateway.
        Returns a dictionary with 'status' and 'raw_response'.
        """
        pass

    @abstractmethod
    def initiate_payment(
        self, amount: float, currency: str, transaction_id: str, description: str
    ) -> dict:
        """
        Initiate a payment and return the gateway's response.
        """
        pass
