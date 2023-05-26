import pytest
from pytest_mysql import factories
from contextlib import contextmanager

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

@pytest.fixture
def connection_factory(your_database, pytestconfig):

    @contextmanager
    def _gen_connection():
        """ Generate a connection to the database """
        import mysql.connector
        from mysql.connector import Error
        # Try to create the connection, if succeeded eventually close it
        connection = mysql.connector.connect(host="127.0.0.1",
                                             database="test",
                                             user="root",
                                             port=pytestconfig.getoption("--mysql-port") if pytestconfig.getoption("--mysql-port") is not None else 3306,
                                             password="mypass")
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)

                yield connection

        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    yield _gen_connection



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


def test_phantom_reads_with_transactions(connection_factory):
    """ Try to concurrently modify the database """
    from solution.user import User
    with connection_factory() as connection1, connection_factory() as connection2:
        cursor1 = connection1.cursor()
        cursor2 = connection2.cursor()

        # Transaction 1 start - Reads all the users, and reads all the users again
        cursor1.execute("BEGIN")
        cursor1.execute("SELECT * FROM User;")
        partial_result_from_transaction_1 = []
        for username, _ in cursor1:
            partial_result_from_transaction_1.append(username)

        # Transaction 2 start - insert a user
        cursor2.execute("BEGIN")
        cursor2.execute(User.INSERT_USER_INTO_DB_TEMPLATE, ("Alice", "123"));
        cursor2.execute("COMMIT")

        cursor1.execute("SELECT * FROM User;")
        final_result_from_transaction_1 = []
        for username, _ in cursor1:
            final_result_from_transaction_1.append(username)
        cursor1.execute("COMMIT")

        assert len(partial_result_from_transaction_1) == len(final_result_from_transaction_1)

def test_sequential_transactions(connection_factory):
    """ Try to concurrently modify the database """
    from solution.user import User
    with connection_factory() as connection1, connection_factory() as connection2:
        cursor1 = connection1.cursor()
        cursor2 = connection2.cursor()

        # Transaction 1 start - Reads all the users
        cursor1.execute("BEGIN")
        cursor1.execute("SELECT * FROM User;")
        partial_result_from_transaction_1 = []
        for username, _ in cursor1:
            partial_result_from_transaction_1.append(username)
        cursor1.execute("COMMIT")

        # Transaction 2 start - insert a user
        cursor2.execute("BEGIN")
        cursor2.execute(User.INSERT_USER_INTO_DB_TEMPLATE, ("Alice", "123"));
        cursor2.execute("COMMIT")

        # Transaction 3 start - Reads all the users
        cursor1.execute("BEGIN")
        cursor1.execute("SELECT * FROM User;")
        final_result_from_transaction_1 = []
        for username, _ in cursor1:
            final_result_from_transaction_1.append(username)
        cursor1.execute("COMMIT")

        assert len(partial_result_from_transaction_1) == 0
        assert len(final_result_from_transaction_1) == 1