import os
import json
import time
from src.parameters.loader import load_parameters
from src.parsers.manager import handle_input_file
from src.openai.manager import handle_ai_content_generation


def print_skill_nicely(learning_skill: dict):
    """
    Utility function to print the generated learning skill in a readable Markdown-like format.
    """
    # Check if the structure contains 'steps'
    if not learning_skill or "steps" not in learning_skill:
        print("No steps found to print.")
        return

    # Iterate through each step
    for step in learning_skill["steps"]:
        print(f"### Step {step.get('step_number')}: {step.get('step_name')}")
        
        # Print the array of image hashes
        image_ids = step.get('image_ids', [])
        print(f"**Images associated with this step (image_ids):** {image_ids}\n")

        widgets = step.get("widgets", {})

        # Print the text content
        for item in widgets.get("contents", []):
            print(f"{item.get('content')}\n")

        # Print Open Questions if they exist
        open_qs = widgets.get("open_questions", [])
        if open_qs:
            print("#### Open Questions:")
            for q in open_qs:
                print(f"- {q}")
            print()

        # Print Multiple Choice Questions if they exist
        mcqs = widgets.get("multiple_choice_questions", [])
        if mcqs:
            print("#### Multiple Choice Questions:")
            for mcq in mcqs:
                print(f"{mcq.get('question')}")
                for opt in mcq.get("options", []):
                    correct_mark = " [Correct Answer]" if opt.get("correct_answer") else ""
                    print(f"- {opt.get('key')}{correct_mark}")
                print()

        # Print Assignments if they exist
        assignments = widgets.get("file_questions", [])
        if assignments:
            print("#### Assignments:")
            for assign in assignments:
                print(f"- {assign}")
            print()
            
        print("---\n")
        
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

        output_dict = handle_input_file(parameters)


        learning_skill = handle_ai_content_generation(output_dict, parameters)

      #  if learning_skill:
          #  print(learning_skill)
        if learning_skill:
            # Use the new formatted print instead of raw JSON
            print_skill_nicely(learning_skill)
     
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
         print( f"Erorr: {e}")

if __name__ == "__main__":
    main()
