from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from trip_agents import TripAgents
from trip_tasks import TripTasks
from crewai import Agent, LLM, Crew
import os
from functools import lru_cache
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app with metadata
app = FastAPI(
    title="TravAgent",
    description="AI-powered travel planning API using CrewAI",
    version="1.0.0"
)

# Enable CORS for all origins (for development/demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request model for trip planning
class TripRequest(BaseModel):
    origin: str = Field(
        ...,
        example="Mumbai, India",
        description="Your current location"
    )
    destination: str = Field(
        ...,
        example="Chicago, USA",
        description="Destination city and country"
    )
    start_date: date = Field(
        ...,
        example="2025-06-10",
        description="Start date of the trip"
    )
    end_date : date = Field(
        ...,
        example="2025-06-15",
        description="End date of the trip"
    )
    interests : str = Field(
        ...,
        example = "2 adults who love cheap hotels, good local food, beaches, trekking",
        description="Your interests and trip details"
    )

# Response model for trip planning
class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Optional[str] = None
    error: Optional[str] = None

# Settings class to load API keys from environment
class Settings:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.SERPER_API_KEY = os.getenv("SERPER_API_KEY")
        self.BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")

# Cached settings loader
@lru_cache()
def get_settings():
    return Settings()

# Main class to orchestrate trip planning using CrewAI
class TripCrew():
    """
    Handles the orchestration of trip planning using CrewAI agents and tasks.
    """
    def __init__(self, origin, cities, date_range, interests):
        self.origin = origin
        self.cities = cities
        self.date_range = date_range
        self.interests = interests
        # Initialize LLM (Language Model) for CrewAI
        self.llm = LLM(model="gemini/gemini-2.0-flash")

    def run(self):
        """
        Runs the trip planning process by initializing agents, tasks, and Crew.
        Returns the generated trip plan or None if an error occurs.
        """
        try:
            # Initialize agent and task classes
            agents = TripAgents()
            tasks = TripTasks()

            # Create agents for different roles
            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
            travel_concierge_agent = agents.travel_concierge()

            # Define tasks for each agent
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

            # Create Crew with agents and tasks
            crew = Crew(
                agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )

            # Run the Crew to generate the itinerary
            result = crew.kickoff()
            return result.raw

        except Exception as e:
            # Raise HTTPException for FastAPI error handling
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# Root endpoint for API health/info
@app.get("/")
async def root():
    return {
        "message":"Welcome to TravAgent API",
        "docs":"/docs",
        "redoc_url":"/redoc"
    }

# Main endpoint to plan a trip
@app.post("/api/v1/plan-trip",response_model=TripResponse)
async def plan_trip(trip_request: TripRequest):
    # Validate date range
    if trip_request.end_date <= trip_request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    # Format date range string
    date_range = f"{trip_request.start_date} to {trip_request.end_date}"

    try:
        # Initialize trip crew and generate itinerary
        trip_crew = TripCrew(
            trip_request.origin,
            trip_request.destination,
            date_range,
            trip_request.interests
        )
        itinerary = trip_crew.run()

        # Return successful response
        return TripResponse(
            status="SUCCESS",
            message="Trip plan generated successfully",
            itinerary = itinerary
        )
    
    except Exception as e:
        # Return error response
        return TripResponse(
            status="error",
            message = "Failed to generate trip plan",
            error = str(e)
        )
    
# Run the app with Uvicorn if executed as main script
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8080)
