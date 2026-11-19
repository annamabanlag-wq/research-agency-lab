"""
Expanded toolset for the Research Agency Lab.
"""

from __future__ import annotations

import os
from typing import List

def build_tools(
    enable_web_search: bool = True,
    enable_arxiv: bool = True,
    enable_code: bool = True,
    enable_files: bool = True,
    enable_scrape: bool = True,
    enable_github: bool = False,
) -> list:
    """Build the full toolset. Gracefully skips unavailable tools."""
    tools: list = []

    try:
        from crewai_tools import (
            SerperDevTool,
            ScrapeWebsiteTool,
            WebsiteSearchTool,
            FileReadTool,
            DirectoryReadTool,
            ArxivPaperTool,
            CodeInterpreterTool,
            PDFSearchTool,
            FileWriterTool,
        )
    except ImportError as e:
        print(f"⚠️  crewai-tools import issue: {e}")
        return tools

    # --- Web Search ---
    if enable_web_search and os.getenv("SERPER_API_KEY"):
        try:
            tools.append(SerperDevTool())
        except Exception as e:
            print(f"SerperDevTool failed: {e}")

    # --- Academic ---
    if enable_arxiv:
        try:
            tools.append(ArxivPaperTool(download_pdfs=False))
        except Exception:
            pass

    # --- Code ---
    if enable_code:
        try:
            tools.append(CodeInterpreterTool())
        except Exception:
            pass

    # --- Files ---
    if enable_files:
        try:
            tools.extend([
                FileReadTool(),
                DirectoryReadTool(),
                FileWriterTool(),
            ])
        except Exception:
            pass

    # --- Scraping ---
    if enable_scrape:
        try:
            tools.extend([ScrapeWebsiteTool(), WebsiteSearchTool()])
        except Exception:
            pass

    # --- GitHub (optional) ---
    if enable_github and os.getenv("GITHUB_TOKEN"):
        try:
            from crewai_tools import GithubSearchTool
            tools.append(GithubSearchTool())
        except Exception:
            pass

    return tools
