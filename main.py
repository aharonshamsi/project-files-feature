import os
import json
#from src.utils.logger import logger
from src.parameters.loader import load_parameters
from src.parsers.manager import handle_input_file
from src.openai.manager import handle_ai_content_generation
import time


def main():
        
    """
    Application entry point.

    High-level flow:
    1. Load runtime parameters from configuration file.
    2. Process the input file (detect type, extract content, generate intermediate output).
    3. Run AI-based content generation on extracted data.
    4. Output final results.

    This file orchestrates the application logic.
    """

    start_time = time.time()
 #   logger.info("Execution started")

    try:

        path_params = "src/parameters/parameters.json"
        parameters = load_parameters(path_params)


        input_file_path = parameters.input_file
        output_file_path = "data/outputs/output.json"
        handle_input_file(input_file_path, output_file_path, parameters)

        learning_skill = handle_ai_content_generation(output_file_path, parameters)

        if learning_skill:
            print(learning_skill)



        # End time
    #     logger.info(
    #         f"Execution completed successfully in {time.time() - start_time:.2f} seconds"
    #     )

    # except (ValueError, FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
    #     logger.error(f"Execution failed: {e}")

    # # except Exception as e:
    # #     logger.error(f"Unexpected error: {e}")
    # except Exception as e:
    #     logger.exception("Unexpected error occurred")
    except Exception as e:
        print("Erorr: " + e)

if __name__ == "__main__":
    main()
