# tests/e2e/task/test_task_flow.py
import os
import uuid
import pytest
from sqlalchemy import create_engine, text
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

pytestmark = pytest.mark.e2e


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def frontend_url():
    """Local file URL to the vanilla Task page."""
    html_file = os.path.join(os.getcwd(), "frontend", "task", "task.html")
    return f"file:///{html_file}"


@pytest.fixture(scope="module")
def api_base():
    """
    Backend base for the Task API.
    Override via env var TASK_API_BASE if you mount differently.
    """
    return os.environ.get("TASK_API_BASE", "http://localhost:8000/kira/app/api/v1/task")

# ---------- Small Selenium helpers ----------
def wait_present(drv, by, value, timeout=8):
    return WebDriverWait(drv, timeout).until(EC.presence_of_element_located((by, value)))


def wait_clickable(drv, by, value, timeout=8):
    return WebDriverWait(drv, timeout).until(EC.element_to_be_clickable((by, value)))


def parents_container(drv):
    return drv.find_element(By.ID, "parents")


def parents_cards(drv):
    return drv.find_elements(By.CSS_SELECTOR, "div.task")


def card_text_contains(card_el, needle: str) -> bool:
    try:
        return needle in card_el.text
    except StaleElementReferenceException:
        return False


def parse_task_id_from_card(card_el):
    """Robust way: read the <div class='task' data-id='123'> attribute."""
    try:
        raw = card_el.get_attribute("data-id")
        return int(raw) if raw and raw.isdigit() else None
    except StaleElementReferenceException:
        return None


def find_card_by_id(drv, task_id, timeout=8):
    """Re-locate a fresh card element by data-id (avoids staleness)."""
    locator = (By.CSS_SELECTOR, f"div.task[data-id='{task_id}']")
    return WebDriverWait(drv, timeout).until(EC.presence_of_element_located(locator))


def _xpath_literal(s: str) -> str:
    """Make an XPath-safe string literal for arbitrary text."""
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    parts = s.split("'")
    return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"


def find_card_by_title(drv, title: str, timeout=8):
    """
    Find a <div class='task'> that contains the given title text anywhere inside it.
    Returns a fresh element (avoids staleness).
    """
    lit = _xpath_literal(title)
    locator = (By.XPATH, f"//div[contains(@class,'task')][.//*[contains(normalize-space(), {lit})]]")
    return WebDriverWait(drv, timeout).until(EC.presence_of_element_located(locator))


def wait_parents_loaded(drv, timeout=8):
    """After pressing 'Load Parents', wait until 'Loading…' disappears."""
    par = parents_container(drv)

    def _done(_):
        try:
            return "Loading…" not in par.text
        except StaleElementReferenceException:
            # If container re-rendered, just re-locate and retry on next poll
            return False

    WebDriverWait(drv, timeout, poll_frequency=0.15).until(_done)


def set_base_url(drv, base_url):
    """Type base URL into #baseUrl and click 'Load Parents'."""
    base = wait_present(drv, By.ID, "baseUrl")
    # Use JS to set value and dispatch a 'change' (page listens for change)
    drv.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
        base,
        base_url,
    )
    wait_clickable(drv, By.ID, "btnLoad").click()
    wait_parents_loaded(drv)


# ---------- Actions that trigger re-render (handle staleness) ----------
def click_status_and_wait(drv, task_id: int, button_label: str, expected_status: str, timeout=8):
    """Click 'Start'/'Block'/'Complete' in a card and wait for status text."""
    card = find_card_by_id(drv, task_id, timeout=timeout)
    btn = card.find_element(By.XPATH, f".//button[normalize-space()='{button_label}']")
    btn.click()
    # The card is replaced via refreshCard -> wait for staleness then re-find
    WebDriverWait(drv, timeout).until(EC.staleness_of(card))
    new_card = find_card_by_id(drv, task_id, timeout=timeout)
    WebDriverWait(drv, timeout, poll_frequency=0.15).until(lambda _: expected_status in new_card.text)
    return new_card


def click_archive_and_wait(drv, task_id: int, detach=False, timeout=8):
    """Click 'Archive' (or 'Archive+Detach' if present) and wait for 'Active: false'."""
    card = find_card_by_id(drv, task_id, timeout=timeout)
    label = "Archive" if not detach else "Archive+Detach"
    btn = card.find_element(By.XPATH, f".//button[contains(normalize-space(), '{label}')]")
    btn.click()
    WebDriverWait(drv, timeout).until(EC.staleness_of(card))
    new_card = find_card_by_id(drv, task_id, timeout=timeout)
    WebDriverWait(drv, timeout, poll_frequency=0.15).until(
        lambda _: "Active: false" in new_card.text or "Active: False" in new_card.text
    )
    return new_card


def click_restore_and_wait(drv, task_id: int, timeout=8):
    """Click 'Restore' and wait for 'Active: true' to appear."""
    card = find_card_by_id(drv, task_id, timeout=timeout)
    btn = card.find_element(By.XPATH, ".//button[normalize-space()='Restore']")
    btn.click()
    WebDriverWait(drv, timeout).until(EC.staleness_of(card))
    new_card = find_card_by_id(drv, task_id, timeout=timeout)
    WebDriverWait(drv, timeout, poll_frequency=0.15).until(
        lambda _: "Active: true" in new_card.text or "Active: True" in new_card.text
    )
    return new_card


# ---------- UI flows (create / edit / attach / detach) ----------
def create_task_via_form(drv, *, title, parent_id=None, priority_bucket: int = 5, status="To-do"):
    drv.find_element(By.ID, "c_title").clear()
    drv.find_element(By.ID, "c_title").send_keys(title)

    # Optional parent_id (create child in one step)
    c_parent = drv.find_element(By.ID, "c_parent")
    c_parent.clear()
    if parent_id is not None:
        c_parent.send_keys(str(parent_id))

    # Priority bucket (1–10)
    pb = max(1, min(10, int(priority_bucket)))
    c_pb = drv.find_element(By.ID, "c_priority_bucket")
    c_pb.clear()
    c_pb.send_keys(str(pb))

    # Status
    drv.find_element(By.ID, "c_status").click()
    drv.find_element(By.XPATH, f"//select[@id='c_status']/option[normalize-space()='{status}']").click()

    drv.find_element(By.ID, "btnCreate").click()
    # The page calls loadParents() after successful POST; wait for it
    wait_parents_loaded(drv)


def open_edit_dialog_for_card(card_el):
    card_el.find_element(By.XPATH, ".//button[normalize-space()='Edit']").click()


def save_edit_dialog(
    drv,
    *,
    title=None,
    description=None,
    priority_bucket: int | None = None,
    start=None,
    due=None,
    project=None,
    active=None,
):
    # Fill whichever fields are provided
    if title is not None:
        e = wait_present(drv, By.ID, "e_title")
        e.clear()
        e.send_keys(title)
    if description is not None:
        e = wait_present(drv, By.ID, "e_desc")
        e.clear()
        e.send_keys(description)
    if priority_bucket is not None:
        e = wait_present(drv, By.ID, "e_priority_bucket")
        e.clear()
        e.send_keys(str(max(1, min(10, int(priority_bucket)))))
    if start is not None:
        e = drv.find_element(By.ID, "e_start")
        e.clear()
        e.send_keys(start)
    if due is not None:
        e = drv.find_element(By.ID, "e_due")
        e.clear()
        e.send_keys(due)
    if project is not None:
        e = drv.find_element(By.ID, "e_project")
        e.clear()
        e.send_keys(str(project))
    if active is not None:
        drv.find_element(By.ID, "e_active").click()
        want = "true" if active else "false"
        drv.find_element(By.XPATH, f"//select[@id='e_active']/option[@value='{want}']").click()

    drv.find_element(By.ID, "btnSaveEdit").click()
    # Wait for dialog to close
    WebDriverWait(drv, 6).until(lambda d: not d.execute_script("return document.getElementById('dlgEdit').open"))


def attach_child_via_card_and_wait(drv, parent_id: int, child_id: int, timeout=8):
    """Type child id into the card's attach field and click 'Attach'."""
    card = find_card_by_id(drv, parent_id, timeout=timeout)
    attach_input = card.find_element(By.XPATH, ".//input[contains(@placeholder,'Attach subtask IDs')]")
    attach_btn = card.find_element(By.XPATH, ".//button[normalize-space()='Attach']")
    attach_input.clear()
    attach_input.send_keys(str(child_id))
    attach_btn.click()
    WebDriverWait(drv, timeout).until(EC.staleness_of(card))
    fresh = find_card_by_id(drv, parent_id, timeout=timeout)
    WebDriverWait(drv, timeout, poll_frequency=0.15).until(lambda _: f"#{child_id}" in fresh.text)
    return fresh


def detach_child_via_card_and_wait(drv, parent_id: int, child_id: int, timeout=8):
    card = find_card_by_id(drv, parent_id, timeout=timeout)
    # Find the subtask row by child id, then its Detach button
    detach_btn = card.find_element(
        By.XPATH,
        f".//*[contains(normalize-space(), '#{child_id}')]//following::button[normalize-space()='Detach'][1]",
    )
    detach_btn.click()
    WebDriverWait(drv, timeout).until(EC.staleness_of(card))
    fresh = find_card_by_id(drv, parent_id, timeout=timeout)
    WebDriverWait(drv, timeout, poll_frequency=0.15).until(lambda _: f"#{child_id}" not in fresh.text)
    return fresh


# E2E-048/001
def test_task_e2e_full_flow(driver, frontend_url, api_base):
    """
    End-to-end happy path using the vanilla HTML page:
      1) Open UI + set Base URL + Load
      2) Create parent
      3) Create child (linked)
      4) Verify child shows under parent
      5) Edit parent title
      6) Start -> Block -> Complete
      7) Detach child
      8) Archive then Restore
    """
    driver.get(frontend_url)
    set_base_url(driver, api_base)

    # Unique titles so we don't depend on DB cleanliness
    parent_title = f"Parent {uuid.uuid4().hex[:6]}"
    child_title = f"Child {uuid.uuid4().hex[:6]}"

    # 2) Create parent
    create_task_via_form(driver, title=parent_title, priority_bucket=5)
    # list auto-reloads; if you want, you can trigger explicit reload too:
    driver.find_element(By.ID, "btnLoad").click()
    wait_parents_loaded(driver)

    # Find our parent (fresh element)
    parent_card = find_card_by_title(driver, parent_title)
    parent_id = parse_task_id_from_card(parent_card)
    assert parent_id is not None, "Could not read data-id from the parent card"

    # 3) Create child (linked on creation)
    create_task_via_form(driver, title=child_title, parent_id=parent_id, priority_bucket=6)
    driver.find_element(By.ID, "btnLoad").click()
    wait_parents_loaded(driver)
    parent_card = find_card_by_id(driver, parent_id)
    assert card_text_contains(parent_card, child_title)

    # 4) Edit parent title
    open_edit_dialog_for_card(parent_card)
    edited_title = f"{parent_title} (edited)"
    save_edit_dialog(driver, title=edited_title, priority_bucket=7)
    driver.find_element(By.ID, "btnLoad").click()
    wait_parents_loaded(driver)
    parent_card = find_card_by_id(driver, parent_id)
    assert card_text_contains(parent_card, edited_title)

    # 5) Status transitions
    parent_card = click_status_and_wait(driver, parent_id, "Start", "In-progress")
    parent_card = click_status_and_wait(driver, parent_id, "Block", "Blocked")
    parent_card = click_status_and_wait(driver, parent_id, "Complete", "Completed")

    # 6) Detach child
    assert child_title in parent_card.text
    # Parse child id from the subtask row line that contains the child title
    child_id = None
    for line in parent_card.text.splitlines():
        if child_title in line and "#" in line:
            try:
                child_id = int(line.split("#")[1].split(" ")[0].strip())
                break
            except Exception:
                pass
    assert child_id is not None, "Could not parse child id from card"
    parent_card = detach_child_via_card_and_wait(driver, parent_id, child_id)
    assert child_title not in parent_card.text

    # 7) Re-attach once to prove attach flow as well
    parent_card = attach_child_via_card_and_wait(driver, parent_id, child_id)
    assert child_title in parent_card.text

    # 8) Archive then Restore
    parent_card = click_archive_and_wait(driver, parent_id, detach=False)
    assert "Active: false" in parent_card.text or "Active: False" in parent_card.text
    parent_card = click_restore_and_wait(driver, parent_id)
    assert "Active: true" in parent_card.text or "Active: True" in parent_card.text
