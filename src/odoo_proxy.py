from .odoo import OdooHelper
from tenacity import *


class OdooProxy:
    """Proxy to work with Odoo. Uses OdooHelper class and exapnds it with retrying decorators."""

    def __init__(self) -> None:
        self.odoo_helper = OdooHelper()

    @retry(wait=wait_fixed(5))
    def create_ticket(self, email: str, robonomics_address_from: str, phone, description: str) -> int:
        """Creats ticket until it will be created.
        :param email: Customer's email address
        :param robonomics_address: Customer's address in Robonomics parachain
        :param phone: Customer's phone number
        :param description: Problem's description from cusotmer

        :return: Ticket id
        """
        self.odoo_helper._logger.debug("Creating ticket...")
        ticket_id = self.odoo_helper.create_ticket(email, robonomics_address_from, phone, description)
        if not ticket_id:
            raise Exception("Failed to create ticket")
        self.odoo_helper._logger.debug(f"Ticket created. Ticket id: {ticket_id}")
        return ticket_id

    @retry(wait=wait_fixed(5))
    def create_note_with_attachment(self, ticket_id: int, file_name: str, file_path: str) -> None:
        """Creats note until it will be created.
        :param ticket_id: Id of the ticket to which logs will be added
        :param file_name: Name of the file
        :param file_path: Path to the file
        """
        self.odoo_helper._logger.debug("Creating note...")
        is_note_created = self.odoo_helper.create_note_with_attachment(ticket_id, file_name, file_path)
        if not is_note_created:
            raise Exception("Failed to create note")
        self.odoo_helper._logger.debug(f"Note created.")
