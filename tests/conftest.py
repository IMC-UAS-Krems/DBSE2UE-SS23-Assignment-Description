import pytest
from pytest_mysql import factories
from contextlib import contextmanager
from neo4j import GraphDatabase
from pytest_mysql.executor_noop import NoopMySQLExecutor


@pytest.fixture(scope="session")
def mariadb_host(request):
    return request.config.getoption("--mysql-host") if request.config.getoption("--mysql-host") is not None else "127.0.0.1"

@pytest.fixture(scope="session")
def mariadb_port(request):
    return request.config.getoption("--mysql-port") if request.config.getoption("--mysql-port") is not None else 3306

# This factory returns instances of connections to mariadb/mysql servers
# mysql_in_docker = factories.mysql_noproc(host=mariadb_host, user="root")

@pytest.fixture(scope="session")
def mariadb_in_docker(mariadb_host, mariadb_port):
	mysql_executor = NoopMySQLExecutor(
            user="root",
            host=mariadb_host,
            port=int(mariadb_port),
        )
    
	with mysql_executor:
         yield mysql_executor

# This creates also a db named test... If I am not mistaked, this is deleted after each test execution
mysql = factories.mysql("mariadb_in_docker", passwd="mypass")


def pytest_addoption(parser):
    """ Register the additional options to make Neo4j Fixtures work also on GitHub Actions """
    try:
        parser.addoption(
            '--neo4j-web-port', action='store', default="", help='Web Port to connect to Neo4j'
        )
        parser.addoption(
            '--neo4j-bolt-port', action='store', default="", help='Bolt Port to connect to Neo4j'
        )
        parser.addoption(
            '--neo4j-host', action='store', default="localhost", help='Bolt Port to connect to Neo4j'
        )
    except Exception:
        pass


@pytest.fixture
def mariadb_database():
    return "test"


@pytest.fixture
def neo4j_db_port(request):
    return request.config.getoption("--neo4j-bolt-port")


@pytest.fixture
def neo4j_db_host(request):
	return request.config.getoption("--neo4j-host")


@pytest.fixture
def mariadb(mysql):
    """
    This fixture creates a db called test initialized with the YOUR code inside the generate_sql_initialization_code
    method
    :param mysql:
    :return:
    """
    from solution.database import generate_sql_initialization_code

    cur = mysql.cursor()
    cur.execute("BEGIN;")
    for sql_statement in generate_sql_initialization_code():
        cur.execute(sql_statement)
    cur.execute("COMMIT;")

    yield mysql


@pytest.fixture
def connection_factory(mariadb_host, mariadb_port, mariadb):
    """ This code retuns an ojbect that can create connections to a database """

    @contextmanager
    def _gen_connection():
        """ Generate a connection to the database """
        import mysql.connector
        from mysql.connector import Error
        # Try to create the connection, if succeeded eventually close it
        connection = mysql.connector.connect(host=mariadb_host,
                                             database="test",
                                             user="root",
                                             port=mariadb_port,
                                             password="mypass")
        try:
            if connection.is_connected():
                db_Info = connection.get_server_info()
                # print("Connected to MariaDB Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                # print("You're connected to database: ", record)

                yield connection

        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                # print("MySQL connection is closed")

    yield _gen_connection


@pytest.fixture
def neo4j_db(neo4j_db_host, neo4j_db_port):
    """
    This fixture connects to a running neo4j database
    :param neo4j_db_host:
    :param neo4j_db_port:
    :return:
    """
    URI = f"neo4j://{neo4j_db_host}:{neo4j_db_port}"

    # Create/Connect to a Database
    with GraphDatabase.driver(URI) as driver:
        driver.verify_connectivity()

        # The community version of Neo4j supports only one database, so we need to remove
        # all the nodes/links before and after each test
        records, summary, keys = driver.execute_query("MATCH (a) DETACH DELETE a")

        yield driver

        records, summary, keys = driver.execute_query("MATCH (a) DETACH DELETE a")
