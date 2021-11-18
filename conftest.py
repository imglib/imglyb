import scyjava
import pytest


@pytest.fixture(scope='session')
def sj_fixture(request):
    """
    Start the JVM through scyjava once for the whole test environment
    :param request: Pytest variable passed in to fixtures
    """
    scyjava.start_jvm()

    yield scyjava
