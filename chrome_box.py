from re import A
from charset_normalizer import detect
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

from util import (
    click_education_save_and_continue,
    click_on_next_page,
    click_work_experience_save_and_continue,
    detect_last_step_and_submit,
    send_request_to_ai_model,
    start_chrome,
    get_to_login_page,
    ask_user_for_job_and_location,
    insert_job_and_location,
    click_into_job_card,
    try_to_click_apply_button,
    click_continue,
    click_on_resume,
    get_questions_and_choices,
    turn_question_mappings_into_ai_prompt,
    close_current_tab_and_switch_back,
    click_on_resume_continue
)

LOAD_DELAY = 4
JOB_CARD_CLASS_NAME = "div.job_seen_beacon"
TESTING_MODE = True


def main():
    driver = start_chrome()
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.indeed.com/viewjob?jk=c1942e0dbbb050b3")

    input("Press if there are no verification page and there is a button.")
    clicked_apply = try_to_click_apply_button(driver)

    if not clicked_apply:
        print("Could not click apply button. Exiting...")
        return

    click_continue(driver, wait)
    click_on_resume(driver, wait)
    click_on_resume_continue(driver, wait)

    time.sleep(LOAD_DELAY)
    buttons = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="continue-button"]')
    if buttons:
        click_on_resume_continue(driver, wait)
        buttons = driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="continue-button"]')

    time.sleep(LOAD_DELAY)
    buttons = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="education-page-review-continue-button"]')
    if buttons:
        click_education_save_and_continue(driver, wait)

    time.sleep(LOAD_DELAY)
    buttons = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="work-experience-page-review-continue-button"]')
    if buttons:
        click_work_experience_save_and_continue(driver, wait)

    if detect_last_step_and_submit(driver, wait):
        print("Application submitted successfully!")
        return

    question_dict = get_questions_and_choices(driver)
    ai_prompt = turn_question_mappings_into_ai_prompt(question_dict)
    ai_response = send_request_to_ai_model(ai_prompt)
    print("AI RESPONSE:")
    print(ai_response)
    return

    get_to_login_page(driver)
    job_title, location = ask_user_for_job_and_location()

    if TESTING_MODE:
        wait = insert_job_and_location(driver)
    else:
        wait = insert_job_and_location(
            driver, job_title=job_title, location=location)
    start_page = 1

    while start_page <= 2:

        time.sleep(LOAD_DELAY)

        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, JOB_CARD_CLASS_NAME))
        )

        for card in cards:
            # a = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
            # title = a.find_element(By.CSS_SELECTOR, "span").text.strip()
            # print(title)
            try:
                title, job_url = click_into_job_card(driver, card, wait)
            except Exception as e:
                print(f"Error occurred while processing card: {e}")
                continue
            input("Press if there are no verification page and there is a button.")
            clicked_apply = try_to_click_apply_button(driver)

            if not clicked_apply:
                ERROR_MSG = f"""
                This job:

                    {title}
                    {job_url}

                does not have an apply button or it could not be clicked. Skipping....
                ----------------------------------------------------------------------
                """

                print(ERROR_MSG)
                close_current_tab_and_switch_back(driver)
                continue

            click_continue(driver, wait)
            click_on_resume(driver, wait)
            question_dict = get_questions_and_choices(driver)
            ai_prompt = turn_question_mappings_into_ai_prompt(question_dict)
            ai_response = send_request_to_ai_model(ai_prompt)
            print("AI RESPONSE:")
            print(ai_response)
            break

        start_page += 1
        click_on_next_page(driver, start_page, wait)


if __name__ == "__main__":
    main()
