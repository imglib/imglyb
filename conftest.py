import scyjava
import pytest


@pytest.fixture(scope="session")
def sj_fixture(request):
    """
    Start the JVM through scyjava once for the whole test environment
    :param request: Pytest variable passed in to fixtures
    """
    scyjava.config.add_option("-Djava.awt.headless=true")
    scyjava.start_jvm()

    yield scyjava
