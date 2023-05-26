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
    └── test_sample.py
```

> **NOTE** the content of this repository may change as the result of in-class discussion or the definition of new public test cases (new files inside the `tests` folder). Make sure you always check out the latest version of this repository from GitHub!

## Task Description

You must develop the backend of an e-commerce platform that sells products stored in various warehouses across the nation.

The backend consists of:

- a relational database (RDBMS) for transactional operations (buy products, register users, etc.) that is implemented using `mariadb`

- a graph database (NoSQL) for recommendations (e.g, suggest products to buy) that is implemented using `neo4j`

### E-Shop Database

### Recommendations
The recommendations system must suggest products that clients are likely to buy after they bought other products.

It has the following API:

`recommend(products, date, limit) -> List[products]`

In a nutshell, given a set of products p1, p2, ..., pn bought by a client c1 on date d1, the system uses the graph database to identify all the products P1, P2, ..., Pk (different than p1, p2, ..., pn) that other clients (c2, ..., cn) have bought together with p1 or p2 or ... pn in the 7 days before the purchase date d1. 

Those products should be sorted by decreasing popularity, i.e., the amount of times they have been bought within 7 days from the purchase date d1. 

Finally, since the amount of products recommended by the system may be very large, the system should return only a limited number of products (`limit`).

For example, given the following list of purchases done by three clients over 6 days

| Client | Date | Cart       |
|--------|------|------------|
|     c1 |   1  | p1, p2     |
|     c2 |   1  | p1, p3     |
|     c2 |   2  | p1, p4     |
|     c3 |   4  | p2, p3, p4 |
|     c1 |   6  | p1, p2     |

The recommendation of a single product for a client that buys p2 and p4 on date 7, i.e.,  `recommend(products=[p2,p4],date=7, limit=1)`, is `[p1]`.

#### Explanation:

The recommendation date is 7, so we need to look at the 7 days before it (6-1).

> NOTE: the recommendation date is excluded

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




