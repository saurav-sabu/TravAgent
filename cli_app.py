import logging
from crewai import Crew, LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks
from datetime import datetime
import argparse
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("trip_planner.log"),
        logging.StreamHandler()
    ]
)

class TripCrew():
    """
    Handles the orchestration of trip planning using CrewAI agents and tasks.
    """
    def __init__(self, origin, cities, date_range, interests):
        self.origin = origin
        self.cities = cities
        self.date_range = date_range
        self.interests = interests
        self.llm = LLM(model="gemini/gemini-2.0-flash")

    def run(self):
        """
        Runs the trip planning process by initializing agents, tasks, and Crew.
        Returns the generated trip plan or None if an error occurs.
        """
        try:
            logging.info("Initializing agents and tasks")
            agents = TripAgents()
            tasks = TripTasks()

            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
            travel_concierge_agent = agents.travel_concierge()

            identify_task = tasks.identity_task(
                city_selector_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range
            )

            gather_task = tasks.gather_task(
                local_expert_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range
            )

            plan_task = tasks.plan_task(
                travel_concierge_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range
            )

            logging.info("Creating Crew and starting trip planning process")
            crew = Crew(
                agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )

            result = crew.kickoff()
            logging.info("Trip planning completed successfully")
            return result

        except Exception as e:
            logging.error(f"An Error Occurred: {str(e)}")
            print(f"An Error Occurred: {str(e)}")
            return None

def validate_date(date_str):
    """
    Validates and parses a date string in YYYY-MM-DD format.
    Raises argparse.ArgumentTypeError if the format is invalid.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD")

def main():
    """
    Entry point for the CLI application.
    Parses arguments, validates input, and triggers trip planning.
    """
    parser = argparse.ArgumentParser(description="AI Travel Planner")

    parser.add_argument('--origin', '-o', type=str, required=True, help="Origin city")
    parser.add_argument('--destination', '-d', type=str, required=True, help="Destination city/cities")
    parser.add_argument('--start-date', '-s', type=validate_date, required=True, help="Trip start date (YYYY-MM-DD)")
    parser.add_argument('--end-date', '-e', type=validate_date, required=True, help="Trip end date (YYYY-MM-DD)")
    parser.add_argument('--interests', '-i', type=str, required=True, help="Travel interests (comma-separated)")

    args = parser.parse_args()

    # Validate date range
    if args.end_date <= args.start_date:
        logging.error("End date must be after start date")
        print("Error: End date must be after start date")
        return

    date_range = f"{args.start_date} to {args.end_date}"

    # Display trip details
    logging.info(f"Planning trip from {args.origin} to {args.destination} ({date_range}), interests: {args.interests}")
    print("\nTravAgent - AI Travel Planner")
    print("------------------------------------------")
    print(f"\nPlanning your trip...")
    print(f"From: {args.origin}")
    print(f"To: {args.destination}")
    print(f"Dates: {date_range}")
    print(f"Interests: {args.interests}")
    print("\nThis may take a few minutes. Creating Travel Plan.......")

    # Initialize and run the trip planner
    trip_crew = TripCrew(args.origin, args.destination, date_range, args.interests)
    result = trip_crew.run()

    # Output the result
    if result:
        logging.info("Trip plan generated successfully")
        print("\nTrip Plan\n-----------------------")
        print(result)
    else:
        logging.error("Failed to generate trip plan")
        print("Failed to generate trip plan")

if __name__ == "__main__":
    main()
