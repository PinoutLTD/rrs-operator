## Robonomics Report Service: Operator. Handles the Reports from Home Assistant

This service uses Odoo [Helpdesk](https://github.com/OCA/helpdesk) module to create tickets and Robonomics Launch as a reports' source. The reports' are sending using Robonomics Launch to the admin account specified in the configuration file. 

---

Requirements:

1. python3.10
2. Odoo with the [Helpdesk](https://github.com/OCA/helpdesk) module installed.
3. Robonomics account ED25519 type.

---

Installation:

```
git clone https://github.com/PinoutLTD/rrs-operator.git
pip3 -r requirements.txt
cp template.env .env
```
Set the configuration file by specifying Odoo and Robonomics credentials.

Launch:
```
python3 main.py
```