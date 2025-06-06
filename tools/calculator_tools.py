from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationInput(BaseModel):
    # The mathematical expression to evaluate, e.g., "2+2"
    operation: str = Field(..., description="The mathematical expression to evaluate")

class CalculatorTools(BaseTool):
    name: str = "Make a calculation"
    description: str = (
        "Useful to perform any mathematical calculations, "
        "like sum, minus, multiplication, division, etc. "
        "The input should be a mathematical expression, e.g. '200*7' or '5000/2*10'."
    )
    args_schema: type[BaseModel] = CalculationInput

    def _run(self, operation: str) -> float:
        """
        Safely evaluates a mathematical expression provided as a string.

        Args:
            operation (str): The mathematical expression to evaluate.

        Returns:
            float: The result of the evaluated expression.
        """
        logger.info(f"Received operation to evaluate: {operation}")
        try:
            # WARNING: Using eval can be dangerous. For production, use a safe parser.
            result = eval(operation)
            logger.info(f"Result of '{operation}' is {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating operation '{operation}': {e}")
            raise
