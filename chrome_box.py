from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time

LOAD_DELAY = 4

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:1559")
chrome_options.add_argument(r'--user-data-dir=C:\temp\chrome_debug_profile')
driver = webdriver.Chrome(options=chrome_options)
print(driver.window_handles)
driver.switch_to.window(driver.window_handles[0])
driver.get("https://www.indeed.com/account/login")

# Getting user to login to their account before proceeding with the job search and application process
input("Waiting for User to Login... Press Enter to continue...")
job_title = input("Enter the job title you want to search for: ")
location = input(
    "Enter the location you want to search for: (e.g. Cambridge, MA, 02139) ")

# locate job position by ID:
wait = WebDriverWait(driver, 10)
job_input_box = wait.until(
    EC.presence_of_element_located((By.ID, "text-input-what")))
print("Job input box found")
job_input_box.clear()
job_input_box.send_keys("software engineer")

location_input_box = wait.until(
    EC.presence_of_element_located((By.ID, "text-input-where")))
print("Location input box found")
location_input_box.click()

# if os is windows:
if driver.capabilities['platformName'].lower() == 'windows':
    location_input_box.send_keys(Keys.CONTROL, "a", Keys.DELETE)
else:
    location_input_box.send_keys(Keys.COMMAND, "a", Keys.DELETE)

location_input_box.send_keys("Cambridge, MA, 02139")

search_btn = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, 'button.yosegi-InlineWhatWhere-primaryButton[type="submit"]')))
search_btn.click()
print("Search button clicked. Waiting for search results to load...")

JOB_CARD_CLASS_NAME = "job_seen_beacon"

time.sleep(LOAD_DELAY)

cards = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.job_seen_beacon")))


def click_apply_button(driver, timeout=10, switch_new_tab=True):
    wait = WebDriverWait(driver, timeout)
    before_handles = driver.window_handles[:]

    # Locate by id or data-testid
    btn = wait.until(EC.element_to_be_clickable((By.ID, "indeedApplyButton")))

    # ensure visible
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", btn)

    # try normal click, fallback to JS
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)


def click_continue(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)

    # robust selector by visible text (works if classes/data-testid vary)
    btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[normalize-space(text())='Continue']]")
    ))

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", btn)
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)

    # wait for either navigation or modal/result change
    wait.until(lambda d: d.execute_script(
        "return document.readyState") == "complete")
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
                lab = question_el.find_element(
                    By.CSS_SELECTOR, f"label[for='{rid}']")
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


def extract_apply_questions(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    cards = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.ia-Questions-item")))
    results = []
    for c in cards:
        try:
            # Prefer the labeled text if present
            label = c.find_element(By.CSS_SELECTOR, "[data-testid$='-label']")
            question_text = label.text.strip()
        except Exception:
            # fallback to any <label> text
            try:
                question_text = c.find_element(
                    By.TAG_NAME, "label").text.strip()
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
                "required": input_el.get_attribute("required") is not None
            }

        results.append({"question": question_text,
                       "field": field})

    return results


for card in cards[:1]:
    a = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
    title = a.find_element(By.CSS_SELECTOR, "span").text.strip()
    href = a.get_attribute("href")
    jk = a.get_attribute("data-jk")
    job_url = f"https://www.indeed.com/viewjob?jk={jk}" if jk else href

    ActionChains(driver).key_down(Keys.COMMAND).click(
        a).key_up(Keys.COMMAND).perform()
    wait.until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])
    wait.until(lambda d: d.execute_script(
        "return document.readyState") == "complete")

    print(f"Opened job: {title} - {job_url}")

    click_apply_button(driver)
    click_continue(driver)
    click_continue(driver)
    questions = extract_apply_questions(driver)
    print("Extracted questions:")
    for q in questions:
        choices = q['field']['type']
        if q['field']['type'] == 'radio':
            input_id = q['field'].get('id') or ''
            input_name = q['field'].get('name') or ''
            q_el = None

            # Prefer locating the input element first (handles special chars), then find its question container
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

            if input_elem is not None:
                # find the nearest ancestor div that matches Indeed's question container classes
                try:
                    q_el = input_elem.find_element(
                        By.XPATH, "./ancestor::div[contains(@class,'mosaic-provider-module-apply-questions-v6n2in') or contains(@class,'ia-Questions-item')][1]")
                except Exception:
                    try:
                        q_el = input_elem.find_element(
                            By.XPATH, "./ancestor::div[1]")
                    except Exception:
                        q_el = None

            radio_choices = []
            if q_el is not None:
                radio_choices = extract_radio_choices(q_el)
            choices = ", ".join(
                [f"{c['label']}({c['value']})" for c in radio_choices])

        print(f" - {q['question']}: {choices}")
