import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime


class TLCDownloader:
    """
    Modular downloader for NYC TLC trip data.
    Supports scraping (fallback) or direct URL generation (recommended).
    Organizes downloads by year subfolders.
    """

    BASE_SCRAPE_URL = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
    BASE_DIRECT_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month:02d}.parquet"

    def __init__(self, base_download_dir="tlc_data", headers=None, use_scrape_fallback=False):
        self.base_download_dir = base_download_dir
        self.use_scrape_fallback = use_scrape_fallback

        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:116.0) "
                "Gecko/20100101 Firefox/116.0"
            )
        }

    def get_folder(self, year):
        folder = os.path.join(self.base_download_dir, f"tlc_{year}")
        os.makedirs(folder, exist_ok=True)
        return folder

    def _fetch_page(self):
        response = requests.get(self.BASE_SCRAPE_URL, headers=self.headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def find_parquet_links(self, year, taxi_types=("yellow", "green")):
        soup = self._fetch_page()
        links = soup.find_all("a", href=True)
        parquet_links = []

        for link in links:
            href = link["href"].lower()
            if (
                any(t in href for t in taxi_types)
                and str(year) in href
                and href.endswith(".parquet")
            ):
                full_url = (
                    link["href"]
                    if link["href"].startswith("http")
                    else "https://www.nyc.gov" + link["href"]
                )
                parquet_links.append(full_url)

        return parquet_links

    def generate_parquet_urls(self, year, taxi_types=("yellow", "green"), months=None):
        if months is None:
            months = range(1, 13)

        urls = []
        now = datetime.now()
        for taxi_type in taxi_types:
            for month in months:
                if (year > now.year) or (year == now.year and month > now.month):
                    continue
                url = self.BASE_DIRECT_URL.format(
                    taxi_type=taxi_type, year=year, month=month
                )
                urls.append(url)
        return urls

    def download_file(self, url, folder):
        """
        Download file only if it exists remotely.
        Uses HEAD first → skips unavailable files gracefully.
        """
        local_filename = os.path.join(folder, url.split("/")[-1])

        if os.path.exists(local_filename):
            print(f"Already exists, skipping: {local_filename}")
            return local_filename

        # Step 1: Check existence with HEAD (fast)
        try:
            head_resp = requests.head(url, headers=self.headers, allow_redirects=True, timeout=10)
            if head_resp.status_code != 200:
                print(f"File not available (HTTP {head_resp.status_code}): {url}")
                return None
        except requests.RequestException as e:
            print(f"HEAD check failed for {url}: {e}")
            return None

        # Step 2: Download if available
        print(f"Downloading: {url} → {local_filename}")
        try:
            with requests.get(url, headers=self.headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))

                with open(local_filename, "wb") as f, tqdm(
                    desc=local_filename,
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bar.update(len(chunk))

            return local_filename

        except requests.HTTPError as e:
            print(f"Download failed (HTTP error): {url} → {e}")
            return None
        except requests.RequestException as e:
            print(f"Download error: {url} → {e}")
            return None

    def download_year(self, year, taxi_types=("yellow", "green"), months=None):
        folder = self.get_folder(year)

        if self.use_scrape_fallback:
            parquet_links = self.find_parquet_links(year=year, taxi_types=taxi_types)
            if parquet_links:
                print(f"Found {len(parquet_links)} scraped links for {year}")
            else:
                print(f"No scraped links → falling back to direct URLs.")
                parquet_links = self.generate_parquet_urls(year, taxi_types, months)
        else:
            parquet_links = self.generate_parquet_urls(year, taxi_types, months)

        print(f"Processing {len(parquet_links)} potential files for {year}")

        downloaded = []
        for url in parquet_links:
            path = self.download_file(url, folder)
            if path:
                downloaded.append(path)

        print(f"Finished {year}. Downloaded/skipped: {len(downloaded)} files.")
        return downloaded