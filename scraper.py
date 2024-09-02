from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_product_details_with_selenium(page_url, pages_to_scrape):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(page_url)
    time.sleep(3)

    product_data = []

    # Loop through the number of pages specified by the user
    for page_number in range(1, pages_to_scrape + 1):
        print(f"Scraping page {page_number}...")

        # Allow time for JavaScript to load the content
        time.sleep(3)

        # Scroll and load all products on the current page
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse the HTML of the current page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all('div', class_='list--gallery--C2f2tvm')

        for product in products:
            name = product.find('h3', class_='multi--titleText--nXeOvyr').text.strip() if product.find('h3', class_='multi--titleText--nXeOvyr') else 'No name available'
            description = product.find('div', class_='multi--content--11nFIBL').get('title', '') if product.find('div', class_='multi--content--11nFIBL') else 'No description available'
            price = product.find('div', class_='multi--price-sale--U-S0jtj').text.strip() if product.find('div', class_='multi--price-sale--U-S0jtj') else 'No price available'
            suppliers = product.find('span', class_='multi--trade--Ktbl2jB').text if product.find('span', class_='multi--trade--Ktbl2jB') else 'Not available'
            
            # Enhanced image extraction with fallback
            image_tag = product.find('img', class_='images--item--3XZa6xf')
            image_url = image_tag['src'] if image_tag and image_tag.get('src') else 'https://via.placeholder.com/100'  # Placeholder image

            # Extracting fractional star rating using the width of the progress bars
            star_divs = product.find_all('div', class_='multi--progress--2E4WzbQ')
            total_width = 0
            for star_div in star_divs:
                if 'style' in star_div.attrs and 'width:' in star_div['style']:
                    try:
                        width_px = star_div['style'].split('width:')[1].split('px')[0].strip()
                        width_value = float(width_px)  # Convert width from string to float
                        total_width += width_value
                    except (ValueError, IndexError):
                        continue
            
            # Assuming each full star is represented by 10px width
            average_review = f"{(total_width / 10):.1f} out of 5 stars" if total_width > 0 else 'No reviews'

            product_data.append({
                'name': name,
                'description': description,
                'price': price,
                'suppliers': suppliers,
                'image_url': image_url,
                'average_review': average_review
            })

        # Try to navigate to the next page using multiple strategies
        try:
            # Try locating the "Next" button by its common attributes or class names
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Next page") or contains(@class, "next-pagination-item")]'))
            )
            next_button.click()
        except Exception as e:
            print(f"Could not find or click the next button: {e}")

            # Alternative strategy: manually build the next page URL if possible
            try:
                next_page_url = f"{page_url}&page={page_number + 1}"
                driver.get(next_page_url)
            except Exception as alt_e:
                print(f"Alternative page navigation failed: {alt_e}")
                break

    driver.quit()

    # Count the number of items scraped
    total_items = len(product_data)
    print(f"Total items scraped: {total_items}")

    return product_data
