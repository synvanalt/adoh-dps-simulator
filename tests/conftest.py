"""Shared pytest fixtures for all test suites."""
import pytest
import tempfile
import shutil
import threading
import time
import socket
from pathlib import Path
from diskcache import Cache
from dash import DiskcacheManager
from simulator.config import Config
from playwright.sync_api import Page, expect


@pytest.fixture
def app_config():
    """Create a test Config with reduced ROUNDS for faster tests."""
    cfg = Config()
    # Reduce simulation rounds for faster tests (default is 15000)
    cfg.ROUNDS = 500
    # Enable damage limit for even faster convergence
    cfg.DAMAGE_LIMIT_FLAG = True
    cfg.DAMAGE_LIMIT = 5000
    return cfg


@pytest.fixture
def fast_app_config():
    """Create a very fast Config for unit tests (minimal rounds)."""
    cfg = Config()
    cfg.ROUNDS = 100
    cfg.DAMAGE_LIMIT_FLAG = True
    cfg.DAMAGE_LIMIT = 2000
    return cfg


@pytest.fixture(scope="module")
def cache():
    """Create a temporary diskcache for tests."""
    # Create temporary directory for cache
    temp_dir = tempfile.mkdtemp(prefix="dash_test_cache_")
    cache_instance = Cache(temp_dir)

    yield cache_instance

    # Cleanup after test
    cache_instance.clear()
    cache_instance.close()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def background_manager(cache):
    """Create a DiskcacheManager for background callback tests."""
    manager = DiskcacheManager(cache)
    return manager


@pytest.fixture
def temp_directory():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp(prefix="dash_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


# Playwright browser configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure Playwright browser launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": True,  # Run in headless mode for CI/CD
        "args": [
            "--disable-dev-shm-usage",  # Avoid shared memory issues
            "--no-sandbox",  # Required for some CI environments
        ]
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


# Dash app fixtures (shared between E2E and UI tests)

def find_free_port():
    """Find a free port for the test server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="module")
def dash_app_port():
    """Get a free port for the Dash app."""
    return find_free_port()


@pytest.fixture(scope="module")
def dash_app_thread(dash_app_port, cache, background_manager):
    """Start Dash app in a background thread."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Import app after adding to path
    import app as dash_app_module

    # Override cache and background manager with test fixtures
    dash_app_module.cache = cache
    dash_app_module.background_callback_manager = background_manager

    # Override Config for faster tests
    dash_app_module.cfg.ROUNDS = 500
    dash_app_module.cfg.DAMAGE_LIMIT_FLAG = True
    dash_app_module.cfg.DAMAGE_LIMIT = 5000

    # Start app in thread
    app = dash_app_module.app

    def run_app():
        app.run(host='127.0.0.1', port=dash_app_port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()

    # Wait for app to start
    time.sleep(3)

    yield app

    # Cleanup handled by daemon thread


@pytest.fixture
def dash_app_url(dash_app_port, dash_app_thread):
    """Get the URL of the running Dash app."""
    return f"http://127.0.0.1:{dash_app_port}"


@pytest.fixture
def dash_page(page: Page, dash_app_url):
    """Navigate to the Dash app and return the page."""
    page.goto(dash_app_url)

    # Wait for main tabs to be ready (this means Dash has rendered)
    page.wait_for_selector("#tabs", timeout=20000)

    # Wait a bit for callbacks to complete
    page.wait_for_timeout(1000)

    yield page


@pytest.fixture
def wait_for_spinner(dash_page: Page):
    """Helper to wait for loading spinner to disappear."""
    def _wait():
        # Wait for loading overlay to hide
        spinner = dash_page.locator("#loading-overlay")
        expect(spinner).to_have_css("display", "none", timeout=30000)
    return _wait


@pytest.fixture
def wait_for_simulation(dash_page: Page):
    """Helper to wait for simulation to complete."""
    def _wait(timeout=60000):
        # Wait for progress modal to disappear
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).not_to_be_visible(timeout=timeout)

        # Wait for results to appear
        results_tab = dash_page.locator("#results-content")
        expect(results_tab).to_be_visible(timeout=5000)
    return _wait
