# DBSE2UE SS23 Assignment Description

## Repo Structure
This repository has the following structure:

```
.
├── README.md
├── __init__.py
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_public.py
    └── test_sample.py

```

> **NOTE** the content of this repository may change as the result of in-class discussion or the definition of new public test cases (new files inside the `tests` folder). Make sure you always check out the latest version of this repository from GitHub!

## Task Description

You must document and develop the backend system of an e-commerce platform that sells products provided by some providers.

The backend system consists of two sub-systems:

- a relational database (RDBMS) for transactional operations (buy products, register users, reporting, etc.). The RDBMS is implemented using `mariadb`

- a graph database (NoSQL) for suggesting products to buy based on current trends. The recommendation system is implemented using `neo4j`

### The RDBMS Database

This database manages informations about users of the system, customers, products, and (completed) orders.

**Users** of the system are the DB Admin/Root that acts as an eShop admin, the registered customers, the product suppliers, and the recommendation system.

**Customers** can be added, removed, and updated. 

> Note: Customer emails **cannot** be update

When a customer is removed, all his/her orders and personal data must wiped out from the system within the next *3* days.

Customer data stored in the RDBMS include their name, surname, email address, date of birth, shipping address (we keep it simple shipping and billing addresses are the same), and credit card number. 

Customers can also register a product wishlist so their can quickly check whether their preferred products are available or not.

The system stores the following **product** information: name, category, price per unit, expiry date, and available units, max units that can be stocked, and supplier. 
> Note: we make the following simplifying assumption: a specific product is supplied by one and only one supplier.

Products can be added, removed, and re-stocked. Restocking a product cannot exceed the max threshold on stocked units.

**Suppliers'** data include name, VAT identification number, and the list of supplied products. 
> Note: Product suppliers' data is unlikely to change; so, the system can only register suppliers and update their supplied product lists, but not remove or update suppliers' data.

#### Products Lookup

Customers can lookup products using their wishlist or by searching for product names, categories, and availability.

> Note: Expired products cannot be sold; thus, they must not show up in customers' lookup.

#### Products Ordering

Customers place orders by specifying the list of products (with their quantities) they want to buy. 

An order completes successfully if all the requested units of products are available (i.e., in stock and not yet expired) and the customer credit card checks out.

> Note: in the available code there's a simple payment gateway mock-up that can be configured to pass/fail. You can use it for testing purposes.

All the information about a successfully completed order must be stored, including order summary, order total, customer information, date of purchase.

If an order fails, then no products should be sold and an error must be reported with the appropriate description: `Not all products are available` or `Payment failed`. Likewise, no information about (failed) orders must be stored.

#### Stats and Reporting

Customers can get their monthly purchase history, i.e., the list of completed orders sorted by their date in a given month.
Completed orders contain the list of products sold (sorted by name), their price, and the overall total.

Suppliers can check how much of their products has been sold in a given month. The system must return to the supplier the list of items sorted by units sold in the given month and whether those products were sold out in that month. (Unsold) expired products must be also reported.

The system must report the list of unavailable items (sold-out and expired) in a given month; so new products can be bought from the suppliers. 

The system can buy products from suppliers; after buying new products, the products become instantaneously available. The system might buy completely new products or re-stock existing ones.

The system reports the top *5* customers that spent the most in a given month, how much did they spent (total), and how many purchases did their do.

#### Hints

1. The API/methods to implement are listed in the given code; however, their parameter lists are kept by design underspecified. For instance, customers are identified by a variable `customer` that may be associated to integer, strings, etc. depending on how you design the database.

2. To complete this assignment, you'll need to make use of the following concepts (some more than once):

- simple and nested transactions for reading, creating, updating and deleting elements from the database;
- queries that makes use of grouping and sorting; 
- transactions with the right isolation level(s)
- consistency checks and foreign keys management (cascade, etc.)
- views;
- users definition and grant permissions;
- database triggers;

### Recommendation System

The recommendation system must suggest products that clients are likely to buy after they bought other products.

The recommendation system is a special user of the RDBMS database. It can read some content from the RDBMS but cannot modify it.

The recommendation system offers the following APIs:

`bulk_update(self, month: int, year: int)`
`recommend(self, products: List, day: int, month: int, year: int, limit: int):`

The call `bulk_update` "imports" data from the RDBMS to build/update the graph. Data may contain duplicate entries; thus, those might be handled properly.

The call `recommend` generates the recommendations. In a nutshell, given a set of products p1, p2, ..., pn bought by a client c1 on date d1, the system uses the graph database to identify all the products P1, P2, ..., Pk (different than p1, p2, ..., pn) that other clients (c2, ..., cn) have bought together with p1 or p2 or ... pn in the *7* days before the purchase date d1.

Those products should be sorted by decreasing popularity, i.e., the amount of times they have been bought within *7* days from the purchase date d1. 

Finally, since the amount of products recommended by the system may be very large, the system should return only a limited number of products (`limit = k`).

For example, given the following list of purchases done by three clients over 6 days

| Client | Date | Cart       |
|--------|------|------------|
|     c1 |   1  | p1, p2     |
|     c2 |   1  | p1, p3     |
|     c2 |   2  | p1, p4     |
|     c3 |   4  | p2, p3, p4 |
|     c1 |   6  | p1, p2     |

The recommendation of a single product for a client that buys p2 and p4 on date 7, i.e.,  `recommend(products=[p2,p4],date=7,limit=1)`, is `[p1]`.

> Note: the syntax is only illustrative!

#### Explanation:

The recommendation date is 7, so we need to look at the 7 days before it (days 1 to 6).

> NOTE: the recommendation date is excluded!

During the period between date 1 and date 6:

- Along with p2:

    - c1 has bought p1 (on date 1)
    - c3 has bought p3, p4 (on date 4)
    - c1 has bought p1 (on date 6)

- Along with p4:

    - c2 has bought p1 (on date 2)
    - c3 has bought p3 (on date 4)

Thus, p1 and p3 have been bought with p2 or p4.

We need to sort p1 and p3 by their popularity:

- p1 has been bought 3 times
    - c1 on date 1
    - c2 on date 2
    - c1 on date 6   
- p3 has been bought 1 time
    - c3 on date 4

Thus, p1 is more popular than p3.

Finally, we return the first (i.e., `limit=1`) of the sorted products, which is p1.




