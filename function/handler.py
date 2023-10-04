from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import boto3


def main(event, context):
    options = Options()
    options.binary_location = "/opt/headless-chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome("/opt/chromedriver", chrome_options=options)

    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
    table = dynamodb.Table("nike-shoes")

    # Target
    url = "https://www.nike.com/w/womens-jordan-shoes-37eefz5e1x6zy7ok"
    driver.get(url)

    # Scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # scroll back
        new_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, arguments[0]);", new_height * 3 / 4)
        time.sleep(2)
        # compare
        print("last_height", last_height)
        print("new_height", new_height)
        if new_height == last_height:
            break
        last_height = new_height

    soup_root = BeautifulSoup(driver.page_source, "html.parser")

    product_links = [
        link["href"]
        for link in soup_root.find_all("a", class_="product-card__link-overlay")
    ]
    print("Total products: ", len(product_links))

    for index, product_link in enumerate(product_links, start=1):
        if product_link.startswith("https://www.nike.com"):
            product_url = product_link
        else:
            product_url = f"https://www.nike.com{product_link}"
        print(f"Analysing {product_url}")
        try:
            driver.get(product_url)
        except Exception as e:
            print(f"Failed to navigate to {product_url}. Error: {e}")
            continue

        # Get ID
        product_id = product_url.split("/")[-1]

        # Parsing HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get name
        product_name_element = soup.find("h1")
        if product_name_element:
            product_name = product_name_element.text.strip()
        else:
            product_name = "Unknown Name"

        # Get sub title
        product_subtitle_element = soup.find("h2", class_="headline-5 pb1-sm d-sm-ib")
        if product_subtitle_element:
            product_subtitle = product_subtitle_element.text.strip()
        else:
            product_subtitle = "Unknown Sub Title"

        # Get description
        product_description_element = soup.find(
            "div", class_="description-preview body-2 css-1pbvugb"
        )
        if product_description_element:
            product_description = product_description_element.find("p").text.strip()
        else:
            product_description = "Unknown Description"

        # Get price
        product_price_element = soup.find(
            "div", class_="product-price css-11s12ax is--current-price css-tpaepq"
        )
        if product_price_element:
            product_price = product_price_element.text.strip()[1:]
            product_price_original = ""
            product_price_discount = ""
        else:
            product_price_element = soup.find(
                "div", class_="product-price is--current-price css-s56yt7 css-xq7tty"
            )
            if product_price_element:
                product_price = product_price_element.text.strip()[1:]
                product_price_original_element = soup.find(
                    "span", class_="visually-hidden"
                )
                product_price_original = ""
                if product_price_original_element:
                    product_price_original = (
                        product_price_original_element.next_sibling.strip()
                    )
                product_price_discount_element = soup.find("span", class_="css-1umcwok")
                product_price_discount = ""
                if product_price_discount_element:
                    product_price_discount = product_price_discount_element.text.strip()
            else:
                product_price = ""
                product_price_original = ""
                product_price_discount = ""

        # Get image
        image_urls_row = [img["src"] for img in soup.find_all("img", {"alt": True})]
        image_urls = [
            url
            for url in image_urls_row
            if product_name.lower().replace(" ", "-").replace(".", "") in url and "t_PDP_1280_v1" in url
        ]
        image_urls = list(set(image_urls))

        # Get size
        size_header_element = soup.find("span", class_="sizeHeader")
        if size_header_element and size_header_element.text.strip() == "ONE SIZE":
            sizes = "ONE SIZE"
        elif size_header_element and size_header_element.text.strip() == "Select Size":
            # size_elements = soup.find_all("input", class_="visually-hidden")
            size_elements = soup.find_all("label", class_="css-xf3ahq")
            size_list = []
            for size_element in size_elements:
                size_text = size_element.text.strip()
                size_list.append(size_text)
            sizes = size_list
        else:
            sizes = "Unknown size"

        # Store item to DynamoDB
        table.put_item(
            Item={
                "id": product_id,
                "name": product_name,
                "subtitle": product_subtitle,
                "description": product_description,
                "price": product_price,
                "size": sizes,
                "images": image_urls,
                "url": product_url,
            }
        )

    driver.close()
    driver.quit()

    response = {"statusCode": 200, "body": "finish"}

    return response
