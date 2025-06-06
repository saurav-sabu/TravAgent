from crewai import Task
from datetime import date
import streamlit as st
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TripTasks():
    """
    A class to generate structured travel planning tasks for CrewAI agents.
    """

    def __validate_inputs(self, origin, cities, interests, date_range):
        """
        Validates that all required input parameters are provided.

        Args:
            origin (str): The traveler's origin city.
            cities (list): List of candidate destination cities.
            interests (list): List of traveler's interests.
            date_range (str): Travel date range or constraints.

        Raises:
            ValueError: If any input parameter is missing.
        """
        logger.info("Validating inputs: origin=%s, cities=%s, interests=%s, date_range=%s", origin, cities, interests, date_range)
        if not origin or not cities or not interests or not date_range:
            logger.error("Validation failed: Missing input parameters")
            raise ValueError("All input parameters must be provided")
        logger.info("Input validation successful")
        return True

    def identity_task(self, agent, origin, cities, interests, date_range):
        """
        Creates a task for selecting the best destination city based on traveler preferences.

        Args:
            agent: The CrewAI agent assigned to this task.
            origin (str): The traveler's origin city.
            cities (list): List of candidate destination cities.
            interests (list): List of traveler's interests.
            date_range (str): Travel date range or constraints.

        Returns:
            Task: Configured CrewAI Task object.
        """
        logger.info("Creating identity_task for agent=%s", agent)
        self.__validate_inputs(origin, cities, interests, date_range)
        logger.info("identity_task: Inputs validated, creating Task object")
        return Task(
            description=f'''
You are a travel expert tasked with selecting the **single best destination city** for a traveler based on their preferences and trip details.

Consider the following:
- **Origin**: {origin}
- **Candidate Cities**: {cities}
- **Traveler Interests**: {interests}
- **Trip Date**: {date_range} (including budget, duration, season, or travel dates)

Your objective is to:
1. Evaluate how well each city aligns with the traveler's interests.
2. Factor in practical constraints such as distance from origin, affordability, seasonal suitability, and overall travel feasibility.
3. Recommend **one ideal city** that offers the best possible experience within the traveler's constraints.

Justify your selection with a short, thoughtful explanation. This recommendation will be used for creating a personalized itinerary.
''',
            expected_output=''' 
A detailed travel recommendation report in the following format:

- **Selected City**: <city_name>
- **Reason for Selection**: A concise explanation of why this city is the best fit based on the traveler's origin, interests, and trip constraints.
- **Weather Forecast**: 3 to 5-day forecast for the travel dates, or general weather conditions during that season.
- **Flight or Travel Ticket Info**: Estimated average round-trip flight or travel cost and duration from the origin city.
- **Accommodation Estimate**: Average cost of staying in the city per night or for the total duration of the trip.
- **Top Experiences**: 3 to 5 recommended attractions or activities that align with the traveler's interests.
- **Local Insights**: Tips or updates relevant to tourists (e.g., safety, local customs, travel advisories).
- **Latest News or Events**: Recent news, upcoming events, or seasonal highlights relevant to the traveler.

Present your output in well-formatted Markdown or clean bullet points for readability.
''',
            agent=agent
        )

    def gather_task(self, agent, origin, cities, interests, date_range):
        """
        Creates a task for gathering local insights and tips for the selected city.

        Args:
            agent: The CrewAI agent assigned to this task.
            origin (str): The traveler's origin city.
            cities (list): List of candidate destination cities.
            interests (list): List of traveler's interests.
            date_range (str): Travel date range or constraints.

        Returns:
            Task: Configured CrewAI Task object.
        """
        logger.info("Creating gather_task for agent=%s", agent)
        self.__validate_inputs(origin, cities, interests, date_range)
        logger.info("gather_task: Inputs validated, creating Task object")
        return Task(
            description=f'''
You are a knowledgeable local guide for the selected destination city. Based on the traveler's origin, interests, and travel range, your job is to provide a well-rounded, insider-level overview of the chosen city.

Inputs:
- **Origin**: {origin}
- **Traveler Interests**: {interests}
- **Trip Range**: {date_range} (may include budget, duration, season, or specific dates)

Your objective is to gather and present essential information that will help the traveler experience the city like a local — confidently and curiously.

Focus on:
1. Neighborhoods that match the traveler's interests.
2. Local tips, cultural etiquette, and dos & don'ts.
3. Popular and hidden spots for food, entertainment, and relaxation.
4. Ongoing or upcoming local events or festivals during the travel period.
5. Any safety considerations or local alerts.

Use your expertise to make this feel like it's coming from someone who knows the city deeply and personally.
''',
            expected_output=''' 
A local insight report for the selected city, structured as follows:

- **Neighborhood Recommendations**: 2-3 neighborhoods that best fit the traveler's interests (e.g., artsy, historic, food-centric, nightlife).
- **Local Tips & Etiquette**: Unique cultural notes, local customs, and behavior expectations.
- **Food & Experience Guide**: Hidden gems, popular eateries, street food zones, markets, or local experiences that tourists might miss.
- **Events & Happenings**: Any current or upcoming local events, festivals, or special activities during the travel window.
- **Safety & Practical Notes**: Area-specific safety tips, scams to avoid, or local transportation hacks.

Structure your output in Markdown or clear bullet points. Your tone should be helpful, local, and genuinely excited to share.
''',
            agent=agent
        )

    def plan_task(self, agent, origin, cities, interests, date_range):
        """
        Creates a task for designing a detailed, personalized travel itinerary.

        Args:
            agent: The CrewAI agent assigned to this task.
            origin (str): The traveler's origin city.
            cities (list): List of candidate destination cities.
            interests (list): List of traveler's interests.
            date_range (str): Travel date range or constraints.

        Returns:
            Task: Configured CrewAI Task object.
        """
        logger.info("Creating plan_task for agent=%s", agent)
        self.__validate_inputs(origin, cities, interests, date_range)
        logger.info("plan_task: Inputs validated, creating Task object")
        return Task(
            description=f'''
You are a world-class travel concierge trusted with designing a seamless and personalized travel plan for a traveler.

Inputs:
- **Origin**: {origin}
- **Candidate Cities**: {cities}
- **Traveler Interests**: {interests}
- **Trip Range**: {date_range} (can include duration, budget, and specific travel dates)

Your task is to:
1. Use the final selected destination city (from previous tasks) as the base.
2. Design a detailed travel itinerary that balances interest-based activities, relaxation, exploration, and logistics.
3. Include local hacks, smart travel tips, and cost-saving suggestions where possible.

Tailor the plan based on the traveler's preferences — whether they seek cultural immersion, nightlife, adventure, nature, or a mix.
''',
            expected_output=''' 
A complete travel itinerary report for the selected city, including:

- **Day-wise Itinerary**: A detailed schedule (morning, afternoon, evening) for each day of the trip, covering attractions, activities, and downtime.
- **Estimated Budget Breakdown**:
    - Flights/Transport
    - Accommodation
    - Daily Meals
    - Activities/Entry Tickets
    - Miscellaneous
- **Packing Suggestions**: Smart packing tips based on the city's weather, culture, and planned activities (e.g., light clothing, power adapter, walking shoes).
- **Local Hacks & Pro Tips**: Time-saving, money-saving, or culturally smart suggestions that improve the travel experience.
- **Safety or Access Considerations** (if applicable): Tips for accessibility, solo travelers, or families.

Format your output in clearly organized sections, using Markdown-style headings or bullet points. The plan should feel curated and practical, like something you’d hand over to a VIP traveler.
''',
            agent=agent
        )
