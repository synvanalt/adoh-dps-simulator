# Testing Guide for ADOH DPS Simulator

This directory contains comprehensive tests for the ADOH DPS Simulator, including unit tests, integration tests, E2E tests, and UI component tests.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures for all tests
├── e2e/                             # End-to-end workflow tests
│   ├── conftest.py                  # E2E-specific fixtures
│   ├── test_complete_dps_workflow.py
│   ├── test_multi_build_workflow.py
│   ├── test_config_reset_workflow.py
│   ├── test_dual_wield_workflow.py
│   └── test_weapon_reference_workflow.py
├── ui/                              # UI component tests
│   ├── conftest.py                  # UI-specific fixtures
│   ├── test_clientside_callbacks.py # JavaScript callback tests
│   ├── test_build_manager_ui.py
│   ├── test_character_settings_ui.py
│   ├── test_additional_damage_ui.py
│   └── test_results_display_ui.py
├── integration/                     # Integration tests (existing)
└── simulator/                       # Simulator unit tests (existing)
```

## Prerequisites

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Playwright Browsers

```bash
playwright install
```

For CI/CD or Docker environments:

```bash
playwright install --with-deps chromium
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

**Unit tests only:**
```bash
pytest tests/simulator/ tests/integration/ -v
```

**E2E tests only:**
```bash
pytest tests/e2e/ -v -m e2e
```

**UI component tests only:**
```bash
pytest tests/ui/ -v -m ui
```

**Clientside callback tests only:**
```bash
pytest tests/ui/test_clientside_callbacks.py -v -m clientside
```

### Run Tests by Marker

```bash
# Run only slow tests
pytest -m slow

# Run only background job tests
pytest -m background

# Run only clientside tests
pytest -m clientside

# Skip slow tests
pytest -m "not slow"
```

### Run Tests in Parallel

```bash
# Use all available CPUs
pytest -n auto

# Use specific number of workers
pytest -n 4
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=callbacks --cov=components --cov=simulator --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

## Playwright-Specific Options

### Browser Selection

```bash
# Run with Chromium (default)
pytest tests/e2e/ --browser chromium

# Run with Firefox
pytest tests/e2e/ --browser firefox

# Run with WebKit (Safari)
pytest tests/e2e/ --browser webkit
```

### Headless vs Headed Mode

```bash
# Headless mode (default, for CI/CD)
pytest tests/e2e/ --headed=false

# Headed mode (see browser, for debugging)
pytest tests/e2e/ --headed=true
```

### Debugging Tests

```bash
# Run with Playwright debugger
PWDEBUG=1 pytest tests/e2e/test_multi_build_workflow.py

# Run specific test with verbose output
pytest tests/e2e/test_multi_build_workflow.py::TestMultiBuildWorkflow::test_add_new_build_workflow -vv

# Run with pdb on failure
pytest tests/e2e/ --pdb
```

### Screenshots and Videos

Playwright automatically captures screenshots on test failure. Find them in:
```
test-results/
```

To enable video recording:
```python
# In conftest.py, add to browser_context_args:
"record_video_dir": "test-results/videos"
```

## Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.e2e` - End-to-end workflow tests
- `@pytest.mark.ui` - UI component tests
- `@pytest.mark.clientside` - JavaScript clientside callback tests
- `@pytest.mark.background` - Background job tests
- `@pytest.mark.slow` - Tests that take >10 seconds
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests

## Writing New Tests

### E2E Test Example

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_my_workflow(dash_page: Page, wait_for_spinner):
    """Test my workflow."""
    # Click button
    btn = dash_page.locator("#my-button")
    btn.click()
    wait_for_spinner()

    # Verify result
    result = dash_page.locator("#result")
    expect(result).to_have_text("Expected Value")
```

### UI Component Test Example

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
def test_my_component(dash_page: Page):
    """Test my UI component."""
    input_field = dash_page.locator("#my-input")
    input_field.fill("test value")

    assert input_field.input_value() == "test value"
```

### Clientside Callback Test Example

```python
import pytest
from playwright.sync_api import Page

@pytest.mark.ui
@pytest.mark.clientside
def test_my_clientside_callback(dash_page: Page, check_no_console_errors):
    """Test clientside callback."""
    # Trigger clientside callback
    btn = dash_page.locator("#trigger-btn")
    btn.click()

    # Verify DOM updated without server call
    result = dash_page.locator("#result")
    assert result.is_visible()

    # No console errors
    # (automatically checked by check_no_console_errors fixture)
```

## Fixtures

### Common Fixtures (tests/conftest.py)

- `app_config()` - Test Config with reduced ROUNDS (500)
- `fast_app_config()` - Very fast Config for unit tests (100 rounds)
- `cache()` - Temporary diskcache for tests
- `background_manager()` - DiskcacheManager for background callbacks
- `browser_type_launch_args()` - Playwright browser configuration
- `browser_context_args()` - Playwright context configuration

### E2E Fixtures (tests/e2e/conftest.py)

- `dash_app_port()` - Free port for Dash app
- `dash_app_thread()` - Background thread running Dash app
- `dash_app_url()` - URL of running Dash app
- `dash_page()` - Playwright page navigated to Dash app
- `wait_for_spinner()` - Wait for loading spinner to hide
- `wait_for_simulation()` - Wait for simulation to complete

### UI Fixtures (tests/ui/conftest.py)

- `mock_simulation_results()` - Mock simulation results
- `fill_character_settings()` - Helper to fill character inputs
- `check_no_console_errors()` - Verify no JavaScript errors

## Performance Optimization

### Speed Up Tests

1. **Reduce simulation rounds:**
   - Tests use `ROUNDS=500` instead of `15000` (default)
   - Set `DAMAGE_LIMIT_FLAG=True` for faster convergence

2. **Run tests in parallel:**
   ```bash
   pytest -n auto
   ```

3. **Skip slow tests during development:**
   ```bash
   pytest -m "not slow"
   ```

4. **Run only specific test files:**
   ```bash
   pytest tests/ui/test_clientside_callbacks.py
   ```

### Prevent Flaky Tests

- Use `expect()` assertions with timeouts instead of `time.sleep()`
- Use `page.wait_for_selector()` for dynamic elements
- Use `wait_for_spinner()` fixture after actions that trigger loading
- Clear browser state between tests (handled automatically)

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### GitHub Actions Jobs

1. **e2e-tests** - E2E workflow tests
2. **ui-tests** - UI component tests
3. **clientside-tests** - JavaScript callback tests
4. **all-tests** - Full test suite with coverage

### Artifacts

On test failure, CI uploads:
- Screenshots (test-results/)
- Test reports
- Coverage reports (HTML)

## Troubleshooting

### Playwright Browser Not Found

```bash
playwright install --with-deps chromium
```

### Tests Hang or Timeout

- Increase timeout in pytest.ini:
  ```ini
  timeout = 300
  ```
- Check for infinite loops in clientside callbacks
- Verify `wait_for_spinner()` is called after async operations

### Port Already in Use

E2E tests automatically find free ports. If issues persist:
```bash
# Kill processes on port 8050
kill $(lsof -t -i:8050)
```

### Test Results Directory Permission Errors

```bash
# Clean up test results
rm -rf test-results/
```

## Best Practices

1. **Use descriptive test names** - Test functions should describe what they test
2. **One assertion per test** - Or closely related assertions
3. **Use fixtures for setup** - Don't repeat setup code
4. **Mark slow tests** - Use `@pytest.mark.slow` for tests >10s
5. **Test both happy and error paths** - Don't just test success cases
6. **Use page object patterns** - For complex UI interactions
7. **Keep tests independent** - Tests should not depend on each other
8. **Clean up after tests** - Use fixtures with yield for cleanup

## Resources

- [Playwright for Python Docs](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [Dash Testing Documentation](https://dash.plotly.com/testing)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)

## Getting Help

If you encounter issues:
1. Check test output for detailed error messages
2. Run with `-vv` for verbose output
3. Use `PWDEBUG=1` to debug Playwright tests
4. Check test-results/ for screenshots
5. Review test logs in CI/CD artifacts
