from src.robonomics import RobonomicsHelper
from src.odoo_proxy import OdooProxy


def main() -> None:
    odoo = OdooProxy()
    robonomics = RobonomicsHelper(odoo)
    robonomics.subscribe()


if __name__ == "__main__":
    main()
