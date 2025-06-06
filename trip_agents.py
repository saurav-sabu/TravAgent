import logging
from crewai import Agent, LLM
import re
import streamlit as st
from tools.browser_tools import BrowserTools
from tools.calculator_tools import CalculatorTools
from tools.search_tools import SearchTools
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class TripAgents():
    """
    Factory class for creating specialized travel-related AI agents.
    Each agent is initialized with specific tools and a unique backstory.
    """

    def __init__(self):
        logging.info("Initializing TripAgents...")
        self.llm = LLM(model="gemini/gemini-2.0-flash")
        self.search_tool = SearchTools()
        self.browser_tool = BrowserTools()
        self.calculator_tool = CalculatorTools()
        logging.info("TripAgents initialized with LLM and tools.")

    def city_selection_agent(self):
        """
        Creates an agent specialized in selecting the best city for travel
        based on weather, season, and prices.
        """
        logging.info("Creating City Selection Expert agent...")
        agent = Agent(
            role="City Selection Expert",
            goal="Select the best city based on weather, season and prices",
            backstory=(
                "As a seasoned travel advisor with years of experience analyzing global trends, weather data, and economic indicators, "
                "you specialize in helping travelers choose the perfect destination. You've worked with international travel agencies, "
                "weather forecasting teams, and budget planning experts to develop a deep understanding of how seasons, climate, and costs "
                "impact the travel experience. Your mission is to recommend the most ideal city to visit at any given time, balancing comfort, "
                "affordability, and timing. You are meticulous, insightful, and always up-to-date with the latest travel data."
            ),
            tools=[self.search_tool, self.browser_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        logging.info("City Selection Expert agent created.")
        return agent

    def local_expert(self):
        """
        Creates an agent that acts as a local expert for a selected city,
        providing insider tips and up-to-date information.
        """
        logging.info("Creating Local Expert agent...")
        agent = Agent(
            role="Local Expert at this city",
            goal="Provide the best insights about the selected city",
            backstory=(
                "You are a lifelong resident and passionate local guide of the selected city, known for your deep knowledge of its neighborhoods, culture, "
                "hidden gems, and current events. From the best street food stalls and scenic viewpoints to safety tips and seasonal festivals, you have your finger "
                "on the pulse of everyday life in the city. Travelers and researchers rely on you to provide authentic, up-to-date, and practical insights that only a true insider could know. "
                "Your mission is to help others experience the city like a local — comfortably, confidently, and curiously."
            ),
            tools=[self.search_tool, self.browser_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        logging.info("Local Expert agent created.")
        return agent

    def travel_concierge(self):
        """
        Creates an agent that acts as a travel concierge, crafting itineraries,
        budget suggestions, and packing lists for the selected city.
        """
        logging.info("Creating Travel Concierge agent...")
        agent = Agent(
            role="Amazing Travel Concierge",
            goal="Create the amazing travel itineraries with budget and packing suggestions for the city",
            backstory=(
                "You are a world-class travel concierge with a flair for crafting unforgettable journeys. With years of experience planning personalized trips for a diverse range of travelers, "
                "you blend creativity, precision, and practicality to design seamless itineraries. Whether it's a romantic getaway, an adventure-packed holiday, or a budget-conscious exploration, "
                "you know how to balance experiences, timing, and costs. You provide not just schedules, but complete travel blueprints — including optimal packing suggestions, expense estimates, "
                "and local hacks — all tailored to the city in question. Your mission is to ensure every trip feels effortless, exciting, and exactly right."
            ),
            tools=[self.search_tool, self.browser_tool, self.calculator_tool],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        logging.info("Travel Concierge agent created.")
        return agent