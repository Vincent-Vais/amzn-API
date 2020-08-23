from proxy import getProxy
from bs4 import BeautifulSoup as bs
import requests
import re

import logging

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# formatter
formatter = logging.Formatter(
    "%(levelname)s - %(asctime)-s - %(filename)s - %(lineno)d --> %(message)s"
)


# stream handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)

# file handler
# fh = logging.FileHandler("logs.log", "w")
# fh.setLevel(level=logging.DEBUG)
# fh.setFormatter(formatter)

# file handler for HTML pages
# fhHTML = logging.FileHandler("pages.html", "w")
# fhHTML.setLevel(level=logging.CRITICAL)
# fhHTML.setFormatter(formatter)

logger.addHandler(sh)
# logger.addHandler(fh)
# logger.addHandler(fhHTML)

logger.disabled = True


def setup():
    logger.info("Entered Setup")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    }
    logger.debug(f"Created headers: {headers}")
    PROXY = getProxy()
    logger.debug(f"Created proxy: {PROXY}")
    proxies = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }
    logger.info(f"Setup is done: {[headers, proxies]}")
    return [headers, proxies]


def scrape(key, page):
    logger.info("Entered Scrape")
    logger.debug(f"Param passed: {key}, {page}")

    logger.debug("Setting up headers and proxies")
    [headers, proxies] = setup()
    logger.debug("Setup is done")
    logger.debug(f"Headers : {headers}")
    logger.debug(f"Proxies : {proxies}")

    logger.debug(f"Created a keyword from param: {key}")

    url = f"https://www.amazon.com/s?k={key}&page={page}"
    logger.debug(f"Url for request: {url}")

    logger.info("Making a request")
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.ok:
        logger.info("Respnose - Ok")

        logger.debug("Parssing HTML")
        page = bs(response.content)
        logger.info("HTML parssed")
        logger.critical(f"{url}:{page.prettify()}")

        logger.debug("Looking for item divs : <div class='a-section a-spacing-medium'>")
        divs = page.find_all(class_="a-section a-spacing-medium")
        logger.debug("Divs")
        results = []
        for div in divs:
            item = {}
            imgDiv = div.find("img", attrs={"data-image-latency": "s-product-image"})
            span = div.find("span", "a-offscreen")
            smallDiv = div.find(class_="a-section a-spacing-none a-spacing-top-micro")
            if smallDiv:
                stars = smallDiv.find(
                    "span", string=re.compile("^\d\.\d\sout of\s\d\sstars$")
                )
                reviewCount = smallDiv.find("span", class_="a-size-base")
            else:
                stars = None
                reviewCount = None
            if imgDiv and span and stars and reviewCount:
                logger.debug("Elements found. Parsing text")
                imgUrl = imgDiv.attrs["src"]
                title = imgDiv.attrs["alt"]
                price = span.get_text()
                rating = stars.get_text()
                reviewsNum = reviewCount.get_text()

                item["img"] = imgUrl
                item["title"] = title
                item["price"] = price
                item["rating"] = rating
                item["reviewsNum"] = reviewsNum

                logger.debug(f"\nITEM CREATED: \n{item}\n")
                results.append(item)
            else:
                logger.warning(f"Problem in : {url}")
                logger.warning(f"imDiv: {imgDiv}")
                logger.warning(f"span: {span}")
                logger.warning(f"smallDiv: {smallDiv}")
                logger.warning(f"stars: {stars}")
                logger.warning(f"reviewCount: {reviewCount}")
                logger.warning("NOT FOUND. CONTINUE SEARCH")
        return results
    else:
        logger.info("Respnose - Failed")
        logger.warning(f"Error code: {response.status_code}")
        return None

