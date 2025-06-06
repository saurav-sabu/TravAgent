from crewai import Crew, LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks
import streamlit as st
import datetime
import sys
from langchain_openai import OpenAI


# Page configuration with custom styling
st.set_page_config(
    page_title="TravAgent - AI Travel Planner",
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9ff 0%, #e6f3ff 100%);
    }
    
    /* Form container */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e8f0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e1e8f0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Status container */
    .status-container {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* Results container */
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.6;
    }
    
    /* Credits styling */
    .credits-container {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
        text-align: center;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)


def create_feature_card(icon, title, description):
    """Create a feature card component"""
    return f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """


class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        # Convert date_range to string format for better handling
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")
        # self.llm = OpenAI(
        #     temperature=0.7,
        #     model_name="gpt-4",
        # )

    def run(self):
        try:
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

          
            crew = Crew(
                agents=[city_selector_agent, local_expert_agent, travel_concierge_agent],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )

            result = crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


# Main App Layout
def main():
    # Header Section
    st.markdown("""
    <div class="main-header">
        <div class="main-title">✈️ TravAgent</div>
        <div class="main-subtitle">Your AI-Powered Travel Planning Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Feature cards
        st.markdown("### 🌟 Why Choose TravAgent?")
        
        st.markdown(create_feature_card(
            "🤖", 
            "AI-Powered Planning",
            "Advanced AI agents work together to create your perfect itinerary"
        ), unsafe_allow_html=True)
        
        st.markdown(create_feature_card(
            "🎯", 
            "Personalized Experience",
            "Tailored recommendations based on your interests and preferences"
        ), unsafe_allow_html=True)
        
        st.markdown(create_feature_card(
            "⚡", 
            "Lightning Fast",
            "Get comprehensive travel plans in minutes, not hours"
        ), unsafe_allow_html=True)

    with col2:
        st.markdown("### 📋 Plan Your Perfect Trip")
        
        # Trip planning form
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            with st.form("trip_form", clear_on_submit=False):
                # Input fields with better styling
                st.markdown("#### 📍 Where are you starting from?")
                location = st.text_input(
                    "",
                    placeholder="e.g., San Francisco, CA",
                    help="Enter your current city or departure location"
                )
                
                st.markdown("#### 🌍 Where would you like to go?")
                cities = st.text_input(
                    "",
                    placeholder="e.g., Tokyo, Japan",
                    help="Enter your dream destination"
                )
                
                # Date selection
                today = datetime.datetime.now().date()
                next_year = today.year + 1
                jan_16_next_year = datetime.date(next_year, 1, 10)
                
                st.markdown("#### 📅 When are you planning to travel?")
                date_range = st.date_input(
                    "",
                    min_value=today,
                    value=(today, jan_16_next_year + datetime.timedelta(days=6)),
                    format="MM/DD/YYYY",
                    help="Select your travel dates"
                )
                
                st.markdown("#### 🎨 Tell us about your interests")
                interests = st.text_area(
                    "",
                    placeholder="e.g., 2 adults who love museums, local cuisine, hiking, and photography. We prefer authentic experiences over tourist traps.",
                    height=100,
                    help="The more details you provide, the better we can customize your trip!"
                )
                
                # Submit button
                col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                with col_submit2:
                    submitted = st.form_submit_button("🚀 Create My Trip Plan", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Processing and Results
    if submitted:
        if not all([location, cities, interests]):
            st.error("🚨 Please fill in all fields to create your travel plan!")
        else:
            # Processing section
            st.markdown('<div class="status-container">', unsafe_allow_html=True)
            with st.status("🤖 **AI Agents are crafting your perfect trip...**", state="running", expanded=True) as status:
                st.markdown("**🔍 City Selection Agent** - Finding the best destinations")
                st.markdown("**🏛️ Local Expert Agent** - Gathering insider knowledge")
                st.markdown("**✈️ Travel Concierge Agent** - Creating your itinerary")
                
                with st.container(height=400, border=True):
                    trip_crew = TripCrew(location, cities, date_range, interests)
                    result = trip_crew.run()
                    st.markdown(result)
                    
                status.update(label="✅ Your personalized trip plan is ready!", state="complete", expanded=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Results section
            if result:
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                st.markdown("## 🗺️ Your Personalized Travel Plan")
                st.markdown("---")
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download option
                st.download_button(
                    label="📄 Download Trip Plan",
                    data=result.raw,
                    file_name=f"TravAgent_Plan_{cities.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

    # Footer with credits
    st.markdown("---")
    st.markdown("""
    <div class="credits-container">
        <h4>🙏 Credits & Acknowledgments</h4>
        <p>Built with ❤️ using <strong>CrewAI</strong> by <a href="https://github.com/saurav-sabu?tab=repositories" target="_blank">@Saurav Sabu</a></p>
        <p>Powered by advanced AI agents and modern web technologies</p>
        <a href="https://github.com/saurav-sabu?tab=repositories" target="_blank">
            <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" 
                 alt="CrewAI Logo" style="width:80px; margin-top: 1rem;"/>
        </a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()