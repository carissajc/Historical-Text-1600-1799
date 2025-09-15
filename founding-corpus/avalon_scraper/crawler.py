from __future__ import annotations
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Set, Dict, Optional, List, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from robotexclusionrulesparser import RobotExclusionRulesParser as Robots
from bs4 import BeautifulSoup
import orjson
import random
import time

from .utils import normalize_url, is_same_site, utc_now_iso
from .extract import extract_text_html, extract_meta_html
from .storage import Storage, DocMeta
from .logging_utils import HumanLogger

USER_AGENT = "AvalonResearchBot/1.0 (contact: you@example.com)"
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 30.0
MAX_CONCURRENCY = 5
BASE = "https://avalon.law.yale.edu/"

@dataclass
class CrawlTask:
    url: str
    parent: Optional[str]


class AvalonCrawler:
    def __init__(self, out_dir: Path, concurrency: int = MAX_CONCURRENCY, delay: float = 0.75):
        self.out_dir = out_dir
        self.storage = Storage(out_dir)
        self.logger = HumanLogger(out_dir)
        self.state = self.storage.load_state()
        self.visited: Dict[str, bool] = self.state.get("visited", {})
        self.outputs: Dict[str, str] = self.state.get("outputs", {})
        self.sem = asyncio.Semaphore(max(1, min(concurrency, MAX_CONCURRENCY)))
        self.delay = delay
        self.session = httpx.AsyncClient(http2=True, headers={"User-Agent": USER_AGENT}, timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT))
        self.robots: Optional[Robots] = None
        self.errors: int = 0
        self.docs_saved: int = 0
        self.pages_visited: int = 0

    async def init_robots(self):
        robots_url = BASE + "robots.txt"
        try:
            r = await self.session.get(robots_url)
            if r.status_code == 200:
                rp = Robots()
                rp.parse(r.text, robots_url)
                self.robots = rp
                self.logger.write("Checked robots.txt and will respect allowed/denied paths.")
            else:
                self.logger.write("robots.txt not accessible; proceeding cautiously.")
        except Exception:
            self.logger.write("robots.txt fetch failed; proceeding cautiously.")

    def allowed(self, url: str) -> bool:
        if self.robots is None:
            return True
        try:
            return self.robots.is_allowed(USER_AGENT, url)
        except Exception:
            return True

    @retry(reraise=True, stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=1, max=10), retry=retry_if_exception_type(httpx.HTTPError))
    async def fetch(self, url: str) -> httpx.Response:
        await asyncio.sleep(self.delay + random.random()*0.5)
        resp = await self.session.get(url)
        if resp.status_code in (408, 429, 500, 502, 503, 504):
            raise httpx.HTTPError(f"Retryable status {resp.status_code}")
        resp.raise_for_status()
        return resp

    def is_index_page(self, html: str, url: str) -> bool:
        soup = BeautifulSoup(html, "lxml")
        # Heuristic: lists of links in content area, little body text
        main_links = soup.select("a")
        long_text = len(soup.get_text(" ", strip=True)) > 2000
        return (len(main_links) >= 10) and not long_text

    async def handle_document(self, url: str, parent: Optional[str], html: str) -> None:
        title, collection, date_text, html_lang = extract_meta_html(html)
        text = extract_text_html(html)
        if not text or len(text.split()) < 50:
            return
        wc = len(text.split()); cc = len(text)
        h = self.storage.compute_hash(text)
        meta = DocMeta(
            url=url,
            title=title or url.rsplit("/",1)[-1],
            collection=collection,
            date_text=date_text,
            html_lang=html_lang,
            retrieved_at=utc_now_iso(),
            parent_url=parent,
            word_count=wc,
            char_count=cc,
            hash=h,
            path=""
        )
        md_path = self.storage.write_markdown(meta, text)
        meta.path = str(md_path)
        self.storage.append_index(meta)
        self.docs_saved += 1
        self.logger.write(f"Saved document '{meta.title}' with {wc:,} words.")

    async def process_page(self, task: CrawlTask, queue: asyncio.Queue[CrawlTask]) -> None:
        url = task.url
        if url in self.visited:
            return
        if not is_same_site(url) or not self.allowed(url):
            return
        try:
            resp = await self.fetch(url)
            self.pages_visited += 1
        except Exception:
            self.errors += 1
            return
        html = resp.text
        soup = BeautifulSoup(html, "lxml")
        # decide type
        if self.is_index_page(html, url):
            # enqueue children
            links = []
            for a in soup.find_all("a", href=True):
                child = normalize_url(a["href"], parent=url)
                if is_same_site(child):
                    links.append(child)
                    await queue.put(CrawlTask(child, url))
            self.logger.write(f"Followed index/list page; discovered {len(links)} links.")
            self.visited[url] = True
            self.storage.save_state({"visited": self.visited, "outputs": self.outputs})
            return
        # likely document page
        await self.handle_document(url, task.parent, html)
        self.visited[url] = True
        self.storage.save_state({"visited": self.visited, "outputs": self.outputs})

    async def crawl(self, seed: str) -> None:
        await self.init_robots()
        q: asyncio.Queue[CrawlTask] = asyncio.Queue()
        await q.put(CrawlTask(seed, None))
        self.logger.write("Visited the 18th-century subject menu; starting crawl.")

        async def worker():
            while True:
                task = await q.get()
                try:
                    async with self.sem:
                        await self.process_page(task, q)
                finally:
                    q.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(self.sem._value)]
        await q.join()
        for w in workers:
            w.cancel()
        self.storage.finalize_parquet()
        self.logger.write(f"Crawl finished. Visited {self.pages_visited} pages; saved {self.docs_saved} documents; {self.errors} errors.")

    async def close(self):
        await self.session.aclose()