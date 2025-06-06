import json
import requests
import streamlit as st
import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchQuery(BaseModel):
    # Defines the schema for the search query argument
    query: str = Field(..., description="The search query to look up")

class SearchTools(BaseTool):
    name: str = "Search the Internet"
    description: str = "Useful to search the internet about the given topic and return relevant results."
    args_schema: type[BaseModel] = SearchQuery

    def _run(self, query: str) -> str:
        """
        Executes a search query using the Serper API and returns formatted results.
        """
        try:
            logger.info(f"Starting search for query: {query}")
            top_results_to_return = 4
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query})
            headers = {
                'X-API-KEY': st.secrets["SERPER_API_KEY"],
                'Content-Type': 'application/json'
            }

            logger.debug(f"Payload: {payload}")
            logger.debug(f"Headers: {headers}")

            response = requests.request("POST", url, headers=headers, data=payload)
            logger.info(f"Search API response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"Search API request failed. Status Code: {response.status_code}")
                return f"Error: Search API request failed. Status Code: {response.status_code}"

            data = response.json()
            logger.debug(f"API response data: {data}")

            if "organic" not in data:
                logger.warning("No 'organic' results found in API response.")
                return "No results found or API error occurred"

            results = data["organic"]
            formatted_results = []

            for result in results[:top_results_to_return]:
                try:
                    formatted_result = "\n".join([
                        f"Title: {result.get('title', 'N/A')}",
                        f"Link: {result.get('link', 'N/A')}",
                        f"Snippet: {result.get('snippet', 'N/A')}",
                        "--------------"
                    ])
                    formatted_results.append(formatted_result)
                    logger.info(f"Added result: {result.get('title', 'N/A')}")
                except Exception as e:
                    logger.error(f"Error formatting result: {e}")
                    continue

            if formatted_results:
                logger.info(f"Returning {len(formatted_results)} formatted results.")
                return "\n".join(formatted_results)
            else:
                logger.warning("No valid result found after formatting.")
                return "No valid result found"
        except Exception as e:
            logger.exception("Error during search")
            return f"Error during search: {str(e)}"
