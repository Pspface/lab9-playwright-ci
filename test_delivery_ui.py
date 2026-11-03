
from pathlib import Path

from playwright.sync_api import Page, expect


HTML_FILE = Path(__file__).parent / "delivery.html"


def open_form(page: Page) -> None:
    page.goto("http://127.0.0.1:8000/delivery.html")


def calculate(page: Page, amount: str, zone: str = "city") -> None:
    page.get_by_label("Сумма заказа (тенге)").fill(amount)
    page.get_by_label("Регион доставки").select_option(zone)
    page.get_by_role("button", name="Рассчитать доставку").click()



def check_result(
    page: Page,
    order: str,
    shipping: str,
    total: str,
) -> None:
    result = page.locator("#result")

    expect(result).to_be_visible()

    expect(page.locator("#order-result")).to_have_text(order)
    expect(page.locator("#shipping-result")).to_have_text(shipping)
    expect(page.locator("#total-result")).to_have_text(total)

    expect(page.get_by_role("alert")).to_be_hidden()



# Тест 1. Город: сумма меньше 10000 тенге.
def test_city_delivery_below_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "9999", "city")
    check_result(page, "9999", "1000", "10999")


# Тест 2. Регион: сумма меньше 10000 тенге.
def test_region_delivery_below_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "9999", "region")
    check_result(page, "9999", "2000", "11999")


# Тест 3. Город: ровно 10000 тенге — доставка бесплатная.
def test_city_delivery_at_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "10000", "city")
    check_result(page, "10000", "0", "10000")


# Тест 4. Регион: ровно 10000 тенге — доставка бесплатная.
def test_region_delivery_at_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "10000", "region")
    check_result(page, "10000", "0", "10000")


# Тест 5. Город: сумма больше 10000 тенге.
def test_city_delivery_above_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "15000", "city")
    check_result(page, "15000", "0", "15000")


# Тест 6. Регион: сумма больше 10000 тенге.
def test_region_delivery_above_threshold(page: Page) -> None:
    open_form(page)
    calculate(page, "15000", "region")
    check_result(page, "15000", "0", "15000")


# Тест 7. Нулевая сумма заказа.
def test_zero_order_amount(page: Page) -> None:
    open_form(page)
    calculate(page, "0", "city")
    check_result(page, "0", "1000", "1000")


# Тест 8. Дробная сумма ниже порога.
def test_decimal_order_amount(page: Page) -> None:
    open_form(page)
    calculate(page, "9999.5", "city")
    check_result(page, "9999.5", "1000", "10999.5")


# Тест 9. Пустое поле суммы.
def test_empty_order_amount(page: Page) -> None:
    open_form(page)
    calculate(page, "", "city")

    expect(page.get_by_role("alert")).to_have_text(
        "Введите сумму заказа."
    )
    expect(page.get_by_role("alert")).to_be_visible()
    expect(page.get_by_role("status")).to_be_hidden()


# Тест 10. Некорректный ввод вместо числа.
def test_invalid_order_amount(page: Page) -> None:
    open_form(page)
    calculate(page, "abc", "city")

    expect(page.get_by_role("alert")).to_have_text(
        "Введите корректное число."
    )
    expect(page.get_by_role("status")).to_be_hidden()


# Тест 11. Отрицательная сумма заказа.
def test_negative_order_amount(page: Page) -> None:
    open_form(page)
    calculate(page, "-100", "region")

    expect(page.get_by_role("alert")).to_have_text(
        "Сумма заказа не может быть отрицательной."
    )
    expect(page.get_by_role("status")).to_be_hidden()


# Тест 12. Смена региона меняет стоимость доставки.
def test_changing_delivery_zone(page: Page) -> None:
    open_form(page)

    calculate(page, "5000", "region")
    check_result(page, "5000", "2000", "7000")

    calculate(page, "5000", "city")
    check_result(page, "5000", "1000", "6000")
