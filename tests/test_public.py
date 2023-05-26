import pytest
from pytest_mysql import factories

# TODO Not the best practice to leave password and the like in-clear!
mysql_in_docker = factories.mysql_noproc(host="127.0.0.1", user="root")
# This creates also a db named test... If I am not mistaked, this is deleted after each test execution
mysql = factories.mysql("mysql_in_docker", passwd="mypass")


@pytest.fixture
def your_database(mysql):
    # Note: This is YOUR code, this code must be list of valid SQL Statements!
    from solution.database import generate_sql_initialization_code

    cur = mysql.cursor()
    cur.execute("BEGIN;")
    for sql_statement in generate_sql_initialization_code():
        cur.execute(sql_statement)
    cur.execute("COMMIT;")

    yield mysql


# Taken from: https://www.tutorialspoint.com/how-to-show-all-the-tables-present-in-the-database-and-server-in-mysql-using-python
def test_user_table_exists(your_database):
    """ This example code shows how to check which tables are in the db."""
    cur = your_database.cursor()
    cur.execute("SHOW TABLES;")
    actual_tables_name = [table_name[0] for table_name in cur]
    # Note: This assertion check ONLY that the User table is there. if you add tables, as you should, their existence
    # will not be ackowledged here
    assert "User" in actual_tables_name


def test_insert_user_does_not_fail(your_database):
    """ Try to insert the new user in an empty database and check that the user is there"""
    from solution.user import User
    new_user = User("Annie", "12344")
    new_user.insert_into_db(your_database)
    actual_users_stored = User.get_all_users_in_db(your_database)

    assert new_user in actual_users_stored


def test_cannot_insert_the_same_user_twice(your_database):
    """ Check it is not possible to insert the same user in an empty database twice, as it violated the PRIMARY KEY """
    from solution.user import User
    new_user = User("Annie", "12344")
    new_user.insert_into_db(your_database)
    with pytest.raises(Exception) as e_info:
        new_user.insert_into_db(your_database)
    assert e_info.typename == "IntegrityError"
