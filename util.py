from selenium.webdriver.support.ui import WebDriverWait


def wait_for_element(driver, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script(
        "return document.readyState") == "complete")

    html = driver.page_source
    return html
