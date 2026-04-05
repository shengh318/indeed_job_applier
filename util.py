import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def start_chrome(
    debugger_address: str = "127.0.0.1:1559",
    profile_dir: str | None = None,
    profile_name: str | None = None,
):
    """Start a Chrome webdriver attached to an existing remote-debugging Chrome.

    - Uses `debugger_address` to attach when provided.
    - `profile_dir` is expanded via `os.path.expanduser`. If not provided,
      a sensible default under the user's home is used.
    - `profile_name` can be set (maps to `--profile-directory`).
    """
    chrome_options = Options()
    if debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)

    if profile_dir is None:
        profile_dir = os.environ.get("CHROME_DEBUG_PROFILE") or os.path.expanduser(
            "~/chrome_debug_profile"
        )
    profile_dir = os.path.expanduser(profile_dir)

    # ensure directory exists
    try:
        os.makedirs(profile_dir, exist_ok=True)
    except Exception:
        # fallback to system temp dir if creation fails
        profile_dir = os.path.join(tempfile.gettempdir(), "chrome_debug_profile")
        os.makedirs(profile_dir, exist_ok=True)

    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    if profile_name is None:
        profile_name = os.environ.get("CHROME_PROFILE_NAME")
    if profile_name:
        chrome_options.add_argument(f"--profile-directory={profile_name}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_to_login_page(driver):
    driver.switch_to.window(driver.window_handles[0])
    driver.get("https://www.indeed.com/account/login")


def ask_user_for_job_and_location():
    input("Waiting for User to Login... Press Enter to continue...")
    job_title = input("Enter the job title you want to search for: ")
    location = input(
        "Enter the location you want to search for: (e.g. Cambridge, MA, 02139) "
    )
    return job_title, location


def insert_job_and_location(
    driver, job_title="software engineer", location="Cambridge, MA, 02139"
):
    wait = WebDriverWait(driver, 10)
    job_input_box = wait.until(
        EC.presence_of_element_located((By.ID, "text-input-what"))
    )
    job_input_box.clear()
    job_input_box.send_keys(job_title)

    location_input_box = wait.until(
        EC.presence_of_element_located((By.ID, "text-input-where"))
    )
    location_input_box.click()

    # if os is windows:
    if driver.capabilities["platformName"].lower() == "windows":
        location_input_box.send_keys(Keys.CONTROL, "a", Keys.DELETE)
    else:
        location_input_box.send_keys(Keys.COMMAND, "a", Keys.DELETE)

    location_input_box.send_keys(location)
    search_btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                'button.yosegi-InlineWhatWhere-primaryButton[type="submit"]',
            )
        )
    )
    search_btn.click()
    print("Search button clicked. Waiting for search results to load...")
    return wait


def click_into_job_card(driver, card, wait):
    a = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
    title = a.find_element(By.CSS_SELECTOR, "span").text.strip()
    href = a.get_attribute("href")
    jk = a.get_attribute("data-jk")
    job_url = f"https://www.indeed.com/viewjob?jk={jk}" if jk else href

    ActionChains(driver).key_down(Keys.COMMAND).click(a).key_up(Keys.COMMAND).perform()
    wait.until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    return title, job_url


def try_to_click_apply_button(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)

    # Only attempt if the apply button exists on the page
    elems = driver.find_elements(By.ID, "indeedApplyButton")
    if not elems:
        return False

    btn = elems[0]

    # wait for it to be clickable (best-effort)
    try:
        wait.until(lambda d: btn.is_displayed() and btn.is_enabled())
    except Exception:
        pass

    # ensure visible
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)

    # try normal click, fallback to JS
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)

    # Do not switch tabs/windows here; caller will handle navigation if needed
    return True


def close_current_tab_and_switch_back(driver):
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def click_continue(driver, wait):
    # robust selector by visible text (works if classes/data-testid vary)
    btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[normalize-space(text())='Continue']]")
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)

    # wait for either navigation or modal/result change
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    return True


def click_on_resume(driver, wait):
    resume = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                '[data-testid="resume-selection-file-resume-radio-card-body"]',
            )
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", resume)
    resume.click()
    return True


def click_on_resume_continue(driver, wait):
    try:
        continue_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="continue-button"]')
            )
        )
    except Exception:
        continue_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[@id='mosaic-provider-module-apply-resume-selection']//button[normalize-space(.)='Continue']",
                )
            )
        )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", continue_btn
    )
    try:
        continue_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", continue_btn)

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    return True


def extract_radio_choices(question_el):
    radios = question_el.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    choices = []
    for r in radios:
        rid = r.get_attribute("id")
        val = r.get_attribute("value")
        label_text = ""

        if rid:
            try:
                lab = question_el.find_element(By.CSS_SELECTOR, f"label[for='{rid}']")
                label_text = lab.text.strip()
            except:
                pass

        if not label_text:
            try:
                parent_label = r.find_element(By.XPATH, "./ancestor::label[1]")
                label_text = parent_label.text.strip()
            except:
                pass

        if not label_text:
            try:
                sib = r.find_element(By.XPATH, "following-sibling::span[1]")
                label_text = sib.text.strip()
            except:
                pass

        choices.append({"id": rid, "value": val, "label": label_text})
    return choices


def find_question_container(driver, input_id=None, input_name=None):
    """Find the nearest question container div for an input by id or name.

    Returns the container WebElement or None.
    """
    input_elem = None
    if input_id:
        try:
            input_elem = driver.find_element(By.ID, input_id)
        except Exception:
            input_elem = None

    if input_elem is None and input_name:
        try:
            input_elem = driver.find_element(By.NAME, input_name)
        except Exception:
            input_elem = None

    if input_elem is None:
        return None

    # Prefer the specific question container class used by Indeed, otherwise fallback to nearest div
    try:
        q_el = input_elem.find_element(
            By.XPATH,
            "./ancestor::div[contains(@class,'mosaic-provider-module-apply-questions-v6n2in') or contains(@class,'ia-Questions-item')][1]",
        )
        return q_el
    except Exception:
        pass

    try:
        return input_elem.find_element(By.XPATH, "./ancestor::div[1]")
    except Exception:
        return None


def get_radio_choices_for_field(field, driver):
    """Given a field dict (from extract_apply_questions), return radio choices for that question only."""
    input_id = field.get("id") if field else None
    input_name = field.get("name") if field else None
    q_el = find_question_container(driver, input_id, input_name)
    if q_el is None:
        return []
    return extract_radio_choices(q_el)


def extract_apply_questions(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ia-Questions-item"))
    )
    results = []
    for c in cards:
        try:
            # Prefer the labeled text if present
            label = c.find_element(By.CSS_SELECTOR, "[data-testid$='-label']")
            question_text = label.text.strip()
        except Exception:
            # fallback to any <label> text
            try:
                question_text = c.find_element(By.TAG_NAME, "label").text.strip()
            except Exception:
                question_text = ""

        # find input/select/textarea if present
        input_el = None
        for tag in ("input", "select", "textarea"):
            try:
                input_el = c.find_element(By.TAG_NAME, tag)
                break
            except Exception:
                input_el = None

        field = {}
        if input_el is not None:
            field = {
                "tag": input_el.tag_name,
                "id": input_el.get_attribute("id"),
                "name": input_el.get_attribute("name"),
                "type": input_el.get_attribute("type"),
                "value": input_el.get_attribute("value"),
                "required": input_el.get_attribute("required") is not None,
            }

        results.append({"question": question_text, "field": field})

    return results


def get_questions_and_choices(driver) -> dict[str, list[dict]]:
    """Extract questions on the apply form and return mapping question -> choices.

    Returns:
        dict: { question_text: [ {label, value, id?}, ... ] }

    Supports radio groups, select dropdowns and checkbox groups. Free-text fields
    return an empty list of choices.
    """
    questions = extract_apply_questions(driver)
    mapping: dict = {}

    for q in questions:
        q_text = q.get("question", "")
        field = q.get("field", {}) or {}
        ftype = field.get("type")
        choices: list[dict] = []

        if ftype == "radio":
            # returns list of {id, value, label}
            choices = get_radio_choices_for_field(field, driver)

        elif ftype == "select":
            q_el = find_question_container(driver, field.get("id"), field.get("name"))
            if q_el is not None:
                try:
                    sel = q_el.find_element(By.TAG_NAME, "select")
                    opts = sel.find_elements(By.TAG_NAME, "option")
                    choices = [
                        {"label": o.text.strip(), "value": o.get_attribute("value")}
                        for o in opts
                    ]
                except Exception:
                    choices = []

        elif ftype == "checkbox":
            # collect checkbox options in the question container
            q_el = find_question_container(driver, field.get("id"), field.get("name"))
            if q_el is not None:
                inputs = q_el.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                for inp in inputs:
                    iid = inp.get_attribute("id")
                    val = inp.get_attribute("value")
                    label_text = ""
                    if iid:
                        try:
                            lab = q_el.find_element(
                                By.CSS_SELECTOR, f"label[for='{iid}']"
                            )
                            label_text = lab.text.strip()
                        except Exception:
                            pass
                    if not label_text:
                        try:
                            parent = inp.find_element(By.XPATH, "./ancestor::label[1]")
                            label_text = parent.text.strip()
                        except Exception:
                            pass
                    choices.append({"id": iid, "value": val, "label": label_text})

        else:
            # free-text, textarea, unknown types -> no structured choices
            choices = "text"

        mapping[q_text] = choices

    return mapping


def turn_question_mappings_into_ai_prompt(
    questions_and_choices: dict[str, list[dict]]
) -> str:
    """Given a mapping of question -> choices, create a prompt for an LLM to answer the questions.

    Example output:

    Question: "What is your highest level of education?"
    Choices:
     - High School (value=high_school)
     - Bachelor's Degree (value=bachelors)
     - Master's Degree (value=masters)
     - Doctorate (value=doctorate)

    Question: "Are you legally authorized to work in the United States?"
    Choices:
     - Yes (value=yes)
     - No (value=no)

    Question: "Please describe your relevant experience."
    Choices:
     - text
    """
    prompt = f"""
    You are applying to a job and need to answer the following application questions. You may use any information from the web to search for relevant information about the company. You are trying to apply to the job so if you need to say things that sounds good for the recruiter, you can say those things as long as they align with the resume skills. For each question, provide the best answer based on the choices given. If the question is free-text, provide a 4 sentence concise and relevant response. Here is the path to the resume that you want to look at:
    
    
    . Return back to me your response in this template:

        1: <your answer to question 1>
        2: <your answer to question 2>
        ...

        Here are the questions and choices:
    """

    for q, choices in questions_and_choices.items():
        prompt += f"Question: {q}\nChoices:\n"
        if isinstance(choices, list):
            for c in choices:
                label = c.get("label", "")
                value = c.get("value", "")
                prompt += f" - {label} (value={value})\n"
        else:
            prompt += " - text\n"
        prompt += "\n"

    return prompt
