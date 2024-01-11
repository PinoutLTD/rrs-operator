from dotenv import load_dotenv
import os
import base64
import xmlrpc.client
import typing as tp
from utils.logger import Logger
from utils.read_file import read_file

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")


class OdooHelper:
    def __init__(self):
        self._logger = Logger("odoo")
        self._connection, self._uid = self._connect_to_db()

    def _connect_to_db(self):
        """Connect to Odoo db

        :return: Proxy to the object endpoint to call methods of the odoo models.
        """
        try:
            common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(ODOO_URL), allow_none=1)
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
            if uid == 0:
                raise Exception("Credentials are wrong for remote system access")
            else:
                self._logger.debug("Connection Stablished Successfully")
                connection = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(ODOO_URL))
                return connection, uid
        except Exception as e:
            self._logger.error(f"Couldn't connect to the db: {e}")

    def create_ticket(
        self, email: str, robonomics_address: str, phone: str, description: str, ipfs_hash: str
    ) -> tp.Optional[int]:
        """Creates ticket in Helpdesk module

        :param email: Customer's email address
        :param robonomics_address: Customer's address in Robonomics parachain
        :param phone: Customer's phone number
        :param description: Problem's description from cusotmer

        :return: Ticket id
        """

        priority = "3"
        channel_id = 5
        name = f"Issue from {robonomics_address}"
        description = f"Hash: {ipfs_hash} .Issue from HA: {description}"
        try:
            ticket_id = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "helpdesk.ticket",
                "create",
                [
                    {
                        "name": name,
                        "description": description,
                        "priority": priority,
                        "channel_id": channel_id,
                        "partner_email": email,
                        "phone": phone,
                    }
                ],
            )
            return ticket_id
        except Exception as e:
            self._logger.error(f"Couldn't create ticket: {e}")
            return None

    def create_note_with_attachment(self, ticket_id: int, file_name: str, file_path: str) -> tp.Optional[bool]:
        """Create log with attachment in Odoo using logs from the customer

        :param ticket_id: Id of the ticket to which logs will be added
        :param file_name: Name of the file
        :param file_path: Path to the file

        :return: If the log note was created or no
        """
        data = read_file(file_path)
        try:
            record = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "mail.message",
                "create",
                [
                    {
                        "body": "Logs from user",
                        "model": "helpdesk.ticket",
                        "res_id": ticket_id,
                    }
                ],
            )
            attachment = self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "ir.attachment",
                "create",
                [
                    {
                        "name": file_name,
                        "datas": base64.b64encode(data).decode(),
                        "res_model": "helpdesk.ticket",
                        "res_id": ticket_id,
                    }
                ],
            )
            return self._connection.execute_kw(
                ODOO_DB,
                self._uid,
                ODOO_PASSWORD,
                "mail.message",
                "write",
                [[record], {"attachment_ids": [(4, attachment)]}],
            )
        except Exception as e:
            self._logger.error(f"Couldn't create note: {e}")
            return None

    def _find_partner_id(self, address: str) -> tp.Union[int, bool]:
        """Find a partner id by the parachain address. This id is used to retrive the partner's email.
        :param address: Partner's address in Robonomics parachain

        :return: The partner id or false.
        """
        id = self._connection.execute_kw(
            ODOO_DB, self._uid, ODOO_PASSWORD, "res.partner", "search", [[("name", "=", address)]]
        )
        self._logger.debug(f"Find partner with id: {id}")
        return id

    def find_partner_email(self, address) -> tp.Optional[str]:
        """Find a partner email.
        :param address: Partner's address in Robonomics parachain

        :return: The partner email or None.
        """
        partner_id = self._find_partner_id(address)
        if partner_id:
            partner_data = self._connection.execute_kw(
                ODOO_DB, self._uid, ODOO_PASSWORD, "res.partner", "read", [partner_id[0]], {"fields": ["email"]}
            )
            email = partner_data[0]["email"]
            self._logger.debug(f"Find partner's email: {email}")
            return email
        else:
            self._logger.error(f"Couldn't find partner for {address}")
