import sys
import os 
import pytest

pytest_plugins = ["docker_compose"]

def is_on_github_actions():
    if "CI" not in os.environ or not os.environ["CI"] or "GITHUB_RUN_ID" not in os.environ:
        return False
    
@pytest.fixture(scope="session")
def skip_macos_and_windows_in_ci():
    is_macos = sys.platform == "darwin"
    is_windows = sys.platform == "win32"
    if is_on_github_actions() and (is_macos or is_windows):
        pytest.skip('skipped on this platform: {}'.format(sys.platform))   
         

@pytest.fixture(scope="session")
def dynamodb_session(skip_macos_and_windows_in_ci, session_scoped_container_getter):
    return session_scoped_container_getter

