from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
from util import (
    start_chrome,
    get_to_login_page,
    ask_user_for_job_and_location,
    insert_job_and_location,
    click_into_job_card,
    try_to_click_apply_button,
    click_continue,
    click_on_resume,
    click_on_resume_continue,
    get_questions_and_choices,
    turn_question_mappings_into_ai_prompt,
    close_current_tab_and_switch_back,
)

LOAD_DELAY = 4
JOB_CARD_CLASS_NAME = "div.job_seen_beacon"
TESTING_MODE = True


def main():
    driver = start_chrome()
    get_to_login_page(driver)
    job_title, location = ask_user_for_job_and_location()

    if TESTING_MODE:
        wait = insert_job_and_location(driver)
    else:
        wait = insert_job_and_location(driver, job_title=job_title, location=location)

    time.sleep(LOAD_DELAY)

    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, JOB_CARD_CLASS_NAME))
    )

    for card in cards[:1]:
        title, job_url = click_into_job_card(driver, card, wait)
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
        click_on_resume_continue(driver, wait)
        question_dict = get_questions_and_choices(driver)
        ai_prompt = turn_question_mappings_into_ai_prompt(question_dict)
        print(ai_prompt)


if __name__ == "__main__":
    main()
