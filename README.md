# Venone CRM

# PROPERTY MANAGEMENT APPLICATION

[![Django Version](https://img.shields.io/badge/Django-Version3-success.svg)](https://www.djangoproject.com)
[![Python Version](https://img.shields.io/badge/Python-3.6-brightgreen.svg)](https://www.python.com)

Description : This software is a rental management and sales software for real estate and land. It includes a mobile application and a web application.

This application includes:
- Real estate management : Real estate agency interfaces
- Listing of managed properties and landlords
- Census of rental units
- Registration of tenants and their assignment to individual rental units (apartments)
- Registration of deposits and advances
- Recording and tracking of rental payments
- Automatic deduction of Management fees every 10th of the month
- Edition of contracts with lessors
- Editing of lease contracts and settlement receipts
- Alert on payment withdrawals and settlement arrears
- Automatic calculation of penalties on late payments after the 15th of the month (penalty 10% of rent)
- Eviction alert after 3 months passed without payment
- Tenants receive alerts by SMS

- Homeowner Interfaces.
All of the above functionality except for the homeowner registration.
NB: Homeowners do not have the ability to initiate legal proceedings. In fact, in case of non-payment over 3 months, homeowners receive the same alerts as our company, the administrator who takes care of informing his bailiffs to initiate the procedure.

- Global Administrator
- Real estate agency management
- Management of homeowners not affiliated with an agency
- Receive delinquency alerts and eviction notices

NB: all alerts are not only receivable by SMS, but also on the software


    "GET" qui va récupérer une ressource en particulier
    "PUT" qui va modifier une ressource.
    "DELETE" qui va supprimer une ressource.
    "PATCH" qui va appliquer une modification partielle d’une ressource.


### Entities:

- User
- Tenant
- House
- Rent
- Payment
- Penaltie

### Relationships:

- User can have multiple tenants.
- House can be rented by multiple tenants.
- Rents are associated with a house and a tenant.
- Payment are associated with a rent.
- Penaltie are associated with a payment.

### Credit

Code: [flavien-hugs](https://twitter.com/flavien_hugs)
