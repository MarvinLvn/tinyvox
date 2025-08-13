import aiohttp
import asyncio
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urljoin, urlparse, quote
import json
from datetime import datetime
import logging

MEDIA_EXTENSIONS = {
    # Audio files
    '.mp3', '.wav', '.m4a', '.aac', '.wma',
    # Video files
    '.mp4', '.mov', '.avi', '.wmv', '.m4v',
    # Transcript files
    '.cha', '.trs', '.txt', '.xml',
    # Archives
    '.zip', '.tar', '.gz', '.7z',
    # Data files
    '.csv', '.xlsx', '.xls'
}


class RunLogger:
    def __init__(self):
        self.log_file = 'script_runs.log'

    def log_run(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"Script run on: {timestamp}\n")


class DownloadState:
    def __init__(self, database):
        self.database = database
        self.base_path = os.path.join('downloaded_corpora', database)

    def mark_completed(self, url):
        pass  # No need to track in JSON anymore

    def is_completed(self, url):
        parsed = urlparse(url)
        rel_path = '/'.join(parsed.path.split('/')[2:])
        rel_path = rel_path.replace('?f=save', '').replace(' ', '_')
        full_path = os.path.join(self.base_path, rel_path)
        return os.path.exists(full_path) and os.path.getsize(full_path) > 0

class Logger:
    def __init__(self, database):
        os.makedirs('logs', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        self.found_logger = logging.getLogger('found_files')
        found_handler = logging.FileHandler(f'logs/found_files_{database}_{timestamp}.txt')
        self.found_logger.addHandler(found_handler)
        self.found_logger.setLevel(logging.INFO)

        self.not_found_logger = logging.getLogger('not_found_files')
        not_found_handler = logging.FileHandler(f'logs/not_found_files_{database}_{timestamp}.txt')
        self.not_found_logger.addHandler(not_found_handler)
        self.not_found_logger.setLevel(logging.INFO)

        self.console_logger = logging.getLogger('console')
        console_handler = logging.StreamHandler()
        self.console_logger.addHandler(console_handler)
        self.console_logger.setLevel(logging.INFO)

    def log_found(self, message):
        self.found_logger.info(message)
        self.console_logger.info(message)

    def log_not_found(self, message):
        self.not_found_logger.info(message)
        self.console_logger.info(message)

    def log_console(self, message):
        self.console_logger.info(message)


async def safe_get(session, url, cookie=None, max_retries=5, logger=None):
    for attempt in range(max_retries):
        try:
            headers = {}
            if cookie:
                headers['Cookie'] = f'talkbank={cookie}'
            async with session.get(url, timeout=None, headers=headers) as response:
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                if logger:
                    logger.log_console(
                        f"Connection error, retry {attempt + 1}/{max_retries} for {url} (waiting {wait_time}s)")
                await asyncio.sleep(wait_time)
            else:
                if logger:
                    logger.log_not_found(f"Failed to connect after {max_retries} attempts: {url}")
                raise


async def explore_media_directory(session, url, cookie, logger, target_corpus=None):
    logger.log_console(f"Exploring directory: {url}")
    try:
        text = await safe_get(session, url, cookie, logger=logger)
        soup = BeautifulSoup(text, 'html.parser')

        files = []
        tasks = []

        for row in soup.find_all('tr'):
            link = row.find('a')
            if not link or not link.get('href'):
                continue

            href = link.get('href')
            if href == '../':
                continue

            # Keep original URL, just remove :443
            full_url = href.replace(':443', '')

            if target_corpus and target_corpus in href:
                logger.log_console(f"Found target corpus directory: {full_url}")

            if '📁' in row.text or href.strip().endswith('/'):
                logger.log_console(f"Found subdirectory: {full_url}")
                tasks.append(explore_media_directory(session, full_url.rstrip('/'), cookie, logger, target_corpus))
            elif any(href.lower().endswith(ext) for ext in MEDIA_EXTENSIONS):
                if not full_url.endswith('?f=save'):
                    full_url += '?f=save'
                files.append(full_url)
                logger.log_found(f"Found file: {full_url}")

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    files.extend(result)

        return files
    except Exception as e:
        logger.log_not_found(f"Error exploring directory {url}: {e}")
        return []


async def download_file(session, url, target_path, cookie, logger, max_retries=5):
    # Replace spaces with underscores in target path
    target_path = target_path.replace(' ', '_')
    logger.log_console(f"Downloading {url} to {target_path}")

    for attempt in range(max_retries):
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Try with URL-encoded spaces first
            encoded_url = url.replace(' ', '%20')
            async with session.get(encoded_url, cookies={'talkbank': cookie}, timeout=None) as response:
                if response.status == 404:
                    # If encoded URL fails, try original URL
                    async with session.get(url, cookies={'talkbank': cookie}, timeout=None) as response2:
                        if response2.status == 404:
                            logger.log_not_found(f"File not found: {url}")
                            return False
                        response = response2

                with open(target_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        if chunk:
                            f.write(chunk)
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                logger.log_console(
                    f"Error, retry {attempt + 1}/{max_retries} for {url}: {str(e)} (waiting {wait_time}s)")
                await asyncio.sleep(wait_time)
            else:
                logger.log_not_found(f"Failed after {max_retries} attempts: {url}: {str(e)}")
                return False

    return False

async def main():
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: ./talkbank_audio_scrapper.py email password database [corpus]")
        print("database can be: homebank, childes, or phon")
        print("Example: ./talkbank_audio_scrapper.py user@example.com password phon Providence")
        print("If no corpus is specified, will download everything from the database")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    database = sys.argv[3].lower()
    target_corpus = sys.argv[4] if len(sys.argv) == 5 else None

    if database not in ['homebank', 'childes', 'phon']:
        print("Database must be one of: homebank, childes, phon")
        sys.exit(1)

    os.makedirs(os.path.join('downloaded_corpora', database), exist_ok=True)

    run_logger = RunLogger()
    run_logger.log_run()

    logger = Logger(database)
    download_state = DownloadState(database)

    conn = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.post(
                    'https://sla2.talkbank.org/logInUser',
                    json={"email": email, "pswd": password},
                    headers={'Content-type': 'application/json'}
            ) as response:
                if not response.ok:
                    logger.log_console("Login failed!")
                    return
                cookie = response.cookies.get('talkbank')
        except Exception as e:
            logger.log_console(f"Login error: {e}")
            return

        logger.log_console(
            f"{'Crawling media files...' if not target_corpus else f'Looking for corpus: {target_corpus}'}")

        media_url = f"https://media.talkbank.org/{database}/"

        try:
            media_files = await explore_media_directory(session, media_url, cookie, logger, target_corpus)

            if media_files:
                logger.log_console(f"Found {len(media_files)} files")
                download_tasks = []

                for file_url in media_files:
                    if download_state.is_completed(file_url):
                        logger.log_console(f"Skipping {file_url} - already downloaded")
                        continue

                    parsed = urlparse(file_url)
                    rel_path = '/'.join(parsed.path.split('/')[2:])
                    rel_path = rel_path.replace('?f=save', '')
                    target_path = os.path.join('downloaded_corpora', database, rel_path)

                    task = download_file(session, file_url, target_path, cookie, logger)
                    download_tasks.append((file_url, task))

                if download_tasks:
                    batch_size = 5
                    for i in range(0, len(download_tasks), batch_size):
                        batch = download_tasks[i:i + batch_size]
                        results = await asyncio.gather(*(task for _, task in batch))
                        for (file_url, _), success in zip(batch, results):
                            if success:
                                download_state.mark_completed(file_url)
                        await asyncio.sleep(1)
            else:
                logger.log_console("No files found")

        except Exception as e:
            logger.log_console(f"Error processing media files: {e}")
            return


if __name__ == "__main__":
    asyncio.run(main())
