"""
Web Automation Module for Kai
Enables real-world task completion: navigating websites, filling forms,
downloading documents, and interacting with web portals.

Use cases:
- Patient portal signup
- Downloading medical forms
- Finding hospital information
- General web research and task completion
"""

import os
import re
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin


class BrowserAutomation:
    """
    Headless browser automation for web tasks.
    Uses Playwright when available, falls back to requests + BeautifulSoup.
    """

    def __init__(self, project_root: str = ""):
        self.project_root = project_root
        self.download_dir = os.path.join(project_root, "downloads")
        self._ensure_download_dir()
        self.driver = None
        self._playwright_available = self._check_playwright()
        self._session_cookies = {}

    def _ensure_download_dir(self):
        os.makedirs(self.download_dir, exist_ok=True)

    def _check_playwright(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False

    def start_browser(self, headless: bool = True) -> Dict[str, Any]:
        """Start a browser session."""
        if self._playwright_available:
            return self._start_playwright(headless)
        return {"success": False, "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"}

    def _start_playwright(self, headless: bool) -> Dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self.driver = self._pw.chromium.launch(headless=headless)
            self.page = self.driver.new_page()
            return {"success": True, "message": "Browser started"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self.driver:
            result = self.start_browser()
            if not result["success"]:
                return result

        try:
            if not url.startswith("http"):
                url = "https://" + url
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            title = self.page.title()
            return {
                "success": True,
                "url": self.page.url,
                "title": title,
                "message": f"Navigated to {title}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search(self, query: str, site: str = "") -> Dict[str, Any]:
        """Search the web and return results."""
        try:
            if site:
                search_url = f"https://www.google.com/search?q=site:{site}+{query.replace(' ', '+')}"
            else:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            result = self.navigate(search_url)
            if not result["success"]:
                return result

            # Extract search results
            results = []
            links = self.page.query_selector_all("div.g")
            for link in links[:10]:
                try:
                    title_el = link.query_selector("h3")
                    url_el = link.query_selector("a")
                    snippet_el = link.query_selector("div.VwiC3b")

                    if title_el and url_el:
                        results.append({
                            "title": title_el.inner_text(),
                            "url": url_el.get_attribute("href"),
                            "snippet": snippet_el.inner_text() if snippet_el else ""
                        })
                except:
                    continue

            return {
                "success": True,
                "results": results,
                "message": f"Found {len(results)} results"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_page_text(self) -> Dict[str, Any]:
        """Get the text content of the current page."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            text = self.page.inner_text("body")
            return {"success": True, "text": text[:5000], "truncated": len(text) > 5000}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_forms(self) -> Dict[str, Any]:
        """Find all forms on the current page."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            forms = self.page.query_selector_all("form")
            form_data = []
            for i, form in enumerate(forms):
                action = form.get_attribute("action") or ""
                method = form.get_attribute("method") or "get"
                inputs = form.query_selector_all("input, select, textarea")
                fields = []
                for inp in inputs:
                    fields.append({
                        "type": inp.get_attribute("type") or "text",
                        "name": inp.get_attribute("name") or "",
                        "id": inp.get_attribute("id") or "",
                        "placeholder": inp.get_attribute("placeholder") or "",
                        "label": self._find_label(inp),
                    })
                form_data.append({
                    "index": i,
                    "action": action,
                    "method": method,
                    "fields": fields
                })
            return {"success": True, "forms": form_data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _find_label(self, element) -> str:
        """Find the label text for a form element."""
        try:
            element_id = element.get_attribute("id")
            if element_id:
                label = self.page.query_selector(f"label[for='{element_id}']")
                if label:
                    return label.inner_text()
            # Try parent label
            parent = element.evaluate("el => el.closest('label')")
            if parent:
                return self.page.evaluate("el => el.innerText", parent)
        except:
            pass
        return ""

    def fill_form(self, form_index: int = 0, data: Dict[str, str] = None) -> Dict[str, Any]:
        """Fill in a form with data."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        data = data or {}
        try:
            forms = self.page.query_selector_all("form")
            if form_index >= len(forms):
                return {"success": False, "error": f"Form {form_index} not found"}

            form = forms[form_index]
            filled = []
            errors = []

            for field_name, value in data.items():
                try:
                    # Try by name
                    el = form.query_selector(f"[name='{field_name}']")
                    if not el:
                        # Try by id
                        el = form.query_selector(f"#{field_name}")

                    if el:
                        tag = el.evaluate("el => el.tagName.toLowerCase()")
                        input_type = el.get_attribute("type") or ""

                        if tag == "select":
                            el.select_option(value)
                        elif input_type == "checkbox":
                            if value.lower() in ("true", "1", "yes", "on"):
                                el.check()
                        elif input_type == "radio":
                            el.click()
                        else:
                            el.fill(value)
                        filled.append(field_name)
                    else:
                        errors.append(f"Field '{field_name}' not found")
                except Exception as fe:
                    errors.append(f"Error filling '{field_name}': {str(fe)}")

            return {
                "success": len(errors) == 0,
                "filled": filled,
                "errors": errors,
                "message": f"Filled {len(filled)} fields" + (f", {len(errors)} errors" if errors else "")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click(self, selector: str) -> Dict[str, Any]:
        """Click an element on the page."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            el = self.page.query_selector(selector)
            if not el:
                # Try text-based click
                el = self.page.get_by_text(selector).first
            if el:
                el.click()
                time.sleep(1)  # Wait for navigation
                return {
                    "success": True,
                    "url": self.page.url,
                    "title": self.page.title(),
                    "message": f"Clicked: {selector}"
                }
            return {"success": False, "error": f"Element not found: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click_link(self, text: str) -> Dict[str, Any]:
        """Click a link by its text content."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            link = self.page.get_by_role("link", name=text).first
            if not link:
                link = self.page.get_by_text(text).first
            if link:
                href = link.get_attribute("href") or ""
                link.click()
                time.sleep(1)
                return {
                    "success": True,
                    "url": self.page.url,
                    "href": href,
                    "message": f"Clicked link: {text}"
                }
            return {"success": False, "error": f"Link not found: {text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_and_click_link(self, text: str) -> Dict[str, Any]:
        """Find a link containing text and click it."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            links = self.page.query_selector_all("a")
            for link in links:
                try:
                    link_text = link.inner_text().lower()
                    if text.lower() in link_text:
                        href = link.get_attribute("href") or ""
                        link.click()
                        time.sleep(1)
                        return {
                            "success": True,
                            "url": self.page.url,
                            "href": href,
                            "matched_text": link.inner_text(),
                            "message": f"Found and clicked: {link.inner_text()}"
                        }
                except:
                    continue
            return {"success": False, "error": f"No link containing '{text}' found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_file(self, url: str = None, filename: str = None) -> Dict[str, Any]:
        """Download a file from a URL or the current page."""
        try:
            if url:
                # Direct download
                import requests
                if not filename:
                    filename = url.split("/")[-1] or "download"
                filepath = os.path.join(self.download_dir, filename)
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                return {
                    "success": True,
                    "path": filepath,
                    "filename": filename,
                    "size": len(resp.content),
                    "message": f"Downloaded: {filename}"
                }
            else:
                # Find downloadable files on current page
                if not self.page:
                    return {"success": False, "error": "No page loaded"}

                pdf_links = self.page.query_selector_all("a[href$='.pdf'], a[href*='download'], a[href*='.doc']")
                files = []
                for link in pdf_links:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    if href:
                        full_url = urljoin(self.page.url, href)
                        files.append({"url": full_url, "text": text})

                if not files:
                    return {"success": False, "error": "No downloadable files found on page"}

                # Download first file
                file_info = files[0]
                return self.download_file(
                    url=file_info["url"],
                    filename=file_info["text"].replace(" ", "_") + ".pdf" if not file_info["url"].endswith(".pdf") else None
                )
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_links(self) -> Dict[str, Any]:
        """Get all links on the current page."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            links = self.page.query_selector_all("a[href]")
            link_list = []
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()
                if href and text:
                    link_list.append({"href": href, "text": text[:100]})
            return {"success": True, "links": link_list[:50]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def take_screenshot(self, filename: str = "screenshot.png") -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        if not self.page:
            return {"success": False, "error": "No page loaded"}

        try:
            filepath = os.path.join(self.download_dir, filename)
            self.page.screenshot(path=filepath, full_page=True)
            return {"success": True, "path": filepath, "message": f"Screenshot saved: {filename}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self):
        """Close the browser."""
        try:
            if self.driver:
                self.driver.close()
            if hasattr(self, '_pw') and self._pw:
                self._pw.stop()
        except:
            pass
        self.driver = None
        self.page = None


class WebResearch:
    """Research helper for finding information and resources online."""

    def __init__(self):
        self.browser = BrowserAutomation()

    def find_hospital_portal(self, hospital_name: str, city: str = "", state: str = "") -> Dict[str, Any]:
        """Find a hospital's patient portal or forms page."""
        query = f"{hospital_name} patient portal"
        if city:
            query += f" {city}"
        if state:
            query += f" {state}"

        result = self.browser.search(query)
        if not result["success"]:
            return result

        # Look for patient portal links
        portal_keywords = ["mychart", "patient portal", "myhealth", "followmyhealth", "cerner", "epic"]
        results = result.get("results", [])

        portal_results = []
        general_results = []

        for r in results:
            url_lower = (r.get("url", "") or "").lower()
            title_lower = (r.get("title", "") or "").lower()
            snippet_lower = (r.get("snippet", "") or "").lower()

            if any(kw in url_lower or kw in title_lower or kw in snippet_lower for kw in portal_keywords):
                portal_results.append(r)
            else:
                general_results.append(r)

        return {
            "success": True,
            "portal_links": portal_results[:5],
            "general_links": general_results[:5],
            "message": f"Found {len(portal_results)} portal links, {len(general_results)} other links"
        }

    def find_patient_forms(self, hospital_name: str, city: str = "", state: str = "") -> Dict[str, Any]:
        """Find downloadable patient forms from a hospital."""
        query = f"{hospital_name} patient release form download pdf"
        if city:
            query += f" {city}"
        if state:
            query += f" {state}"

        result = self.browser.search(query)
        if not result["success"]:
            return result

        # Filter for PDF links
        pdf_results = []
        for r in result.get("results", []):
            url = (r.get("url", "") or "").lower()
            title = (r.get("title", "") or "").lower()
            snippet = (r.get("snippet", "") or "").lower()

            if ".pdf" in url or "form" in title or "form" in snippet or "download" in title:
                pdf_results.append(r)

        return {
            "success": True,
            "form_links": pdf_results[:5],
            "all_results": result.get("results", [])[:10],
            "message": f"Found {len(pdf_results)} potential form links"
        }

    def get_hospital_info(self, hospital_name: str, city: str = "", state: str = "") -> Dict[str, Any]:
        """Get general hospital information including address, phone, website."""
        query = f"{hospital_name} {city} {state} hospital contact information"
        result = self.browser.search(query)

        if not result["success"]:
            return result

        return {
            "success": True,
            "results": result.get("results", [])[:5],
            "message": f"Found information about {hospital_name}"
        }

    def close(self):
        self.browser.close()


class TaskExecutor:
    """
    High-level task executor that breaks natural language tasks into steps.
    """

    def __init__(self, project_root: str = ""):
        self.project_root = project_root
        self.browser = BrowserAutomation(project_root)
        self.research = WebResearch()
        self.task_history = []

    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Parse a natural language task and execute it.
        Returns step-by-step results.
        """
        task_lower = task_description.lower()
        steps = []

        # Detect task type
        if self._is_form_download_task(task_lower):
            return self._handle_form_download(task_description)
        elif self._is_portal_signup_task(task_lower):
            return self._handle_portal_signup(task_description)
        elif self._is_research_task(task_lower):
            return self._handle_research(task_description)
        else:
            return self._handle_general_web_task(task_description)

    def _is_form_download_task(self, task: str) -> bool:
        keywords = ["form", "download", "release", "paperwork", "document", "pdf"]
        return any(kw in task for kw in keywords)

    def _is_portal_signup_task(self, task: str) -> bool:
        keywords = ["portal", "sign up", "register", "account", "login", "patient portal"]
        return any(kw in task for kw in keywords)

    def _is_research_task(self, task: str) -> bool:
        keywords = ["find", "search", "look up", "what is", "information about"]
        return any(kw in task for kw in keywords)

    def _extract_hospital_info(self, task: str) -> Tuple[str, str, str]:
        """Extract hospital name, city, and state from task description."""
        hospital_name = ""
        city = ""
        state = ""

        # Common hospital name patterns
        hospital_patterns = [
            r"(st\.?\s*\w+(?:'s)?(?:\s+\w+)*)",
            r"((?:\w+\s+)*hospital)",
            r"((?:\w+\s+)*medical\s*(?:center|centre))",
            r"((?:\w+\s+)*health\s*(?:system|center|centre))",
            r"(st\.\s*jude)",
            r"(mayo\s*clinic)",
            r"(cleveland\s*clinic)",
        ]

        for pattern in hospital_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                hospital_name = match.group(1).strip()
                break

        # State abbreviations and names
        state_match = re.search(r'\b([A-Z]{2})\b|' +
            r'\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|' +
            r'hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|' +
            r'michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|' +
            r'new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|' +
            r'rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|' +
            r'washington|west virginia|wisconsin|wyoming)\b',
            task, re.IGNORECASE)
        if state_match:
            state = state_match.group(0)

        # City - look for "in <city>" pattern
        city_match = re.search(r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', task)
        if city_match:
            city = city_match.group(1)

        return hospital_name, city, state

    def _handle_form_download(self, task: str) -> Dict[str, Any]:
        """Handle downloading a form from a hospital website."""
        hospital_name, city, state = self._extract_hospital_info(task)
        results = {"steps": [], "files": [], "success": False}

        # Step 1: Find the forms page
        results["steps"].append({
            "action": "search",
            "description": f"Searching for {hospital_name} patient forms"
        })

        search_result = self.research.find_patient_forms(hospital_name, city, state)
        results["steps"].append({
            "action": "search_complete",
            "description": search_result.get("message", ""),
            "data": search_result.get("form_links", [])
        })

        if search_result.get("form_links"):
            # Step 2: Navigate to first result
            first_link = search_result["form_links"][0]
            url = first_link.get("url", "")

            if url.endswith(".pdf"):
                # Direct PDF download
                dl_result = self.browser.download_file(url)
                results["steps"].append({
                    "action": "download",
                    "description": dl_result.get("message", ""),
                    "data": dl_result
                })
                if dl_result["success"]:
                    results["files"].append(dl_result.get("path", ""))
                    results["success"] = True
            else:
                # Navigate and find download link
                nav_result = self.browser.navigate(url)
                results["steps"].append({
                    "action": "navigate",
                    "description": nav_result.get("message", ""),
                    "url": nav_result.get("url", "")
                })

                # Try to find and download forms
                dl_result = self.browser.download_file()
                results["steps"].append({
                    "action": "download",
                    "description": dl_result.get("message", ""),
                    "data": dl_result
                })
                if dl_result["success"]:
                    results["files"].append(dl_result.get("path", ""))

        self.task_history.append({"task": task, "results": results})
        return results

    def _handle_portal_signup(self, task: str) -> Dict[str, Any]:
        """Handle finding and navigating to a patient portal signup."""
        hospital_name, city, state = self._extract_hospital_info(task)
        results = {"steps": [], "success": False}

        results["steps"].append({
            "action": "search",
            "description": f"Finding {hospital_name} patient portal"
        })

        portal_result = self.research.find_hospital_portal(hospital_name, city, state)
        results["steps"].append({
            "action": "search_complete",
            "description": portal_result.get("message", ""),
            "data": portal_result.get("portal_links", [])
        })

        if portal_result.get("portal_links"):
            first_portal = portal_result["portal_links"][0]
            url = first_portal.get("url", "")

            nav_result = self.browser.navigate(url)
            results["steps"].append({
                "action": "navigate",
                "description": nav_result.get("message", ""),
                "url": nav_result.get("url", ""),
                "title": nav_result.get("title", "")
            })

            # Look for sign up / register link
            if nav_result["success"]:
                signup_result = self.browser.find_and_click_link("sign up")
                if not signup_result["success"]:
                    signup_result = self.browser.find_and_click_link("register")
                if not signup_result["success"]:
                    signup_result = self.browser.find_and_click_link("create account")
                if not signup_result["success"]:
                    signup_result = self.browser.find_and_click_link("new user")

                results["steps"].append({
                    "action": "find_signup",
                    "description": signup_result.get("message", signup_result.get("error", "")),
                    "url": signup_result.get("url", "")
                })

                # Get the page text so user can see what's there
                page_text = self.browser.get_page_text()
                results["page_content"] = page_text.get("text", "")[:2000]
                results["portal_url"] = self.browser.page.url if self.browser.page else ""
                results["success"] = True

        self.task_history.append({"task": task, "results": results})
        return results

    def _handle_research(self, task: str) -> Dict[str, Any]:
        """Handle general research tasks."""
        results = {"steps": [], "success": False}

        search_result = self.browser.search(task)
        results["steps"].append({
            "action": "search",
            "description": search_result.get("message", ""),
            "data": search_result.get("results", [])[:5]
        })
        results["search_results"] = search_result.get("results", [])[:10]
        results["success"] = search_result["success"]

        self.task_history.append({"task": task, "results": results})
        return results

    def _handle_general_web_task(self, task: str) -> Dict[str, Any]:
        """Handle general web tasks."""
        return self._handle_research(task)

    def close(self):
        self.browser.close()
        self.research.close()
