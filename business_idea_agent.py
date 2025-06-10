import openai
import os
import json
import whois
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

# It's good practice to load the API key from an environment variable
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("Please set the OPENAI_API_KEY environment variable.")
# openai.api_key = OPENAI_API_KEY

def generate_idea(business_domain: str, api_key: str) -> dict:
    """
    Generates an innovative business idea within the given domain using OpenAI.

    Args:
        business_domain (str): The business domain (e.g., "health and fitness").
        api_key (str): The OpenAI API key.

    Returns:
        dict: A dictionary containing:
            - businessName (str)
            - businessDescription (str)
            - tagline (str)
    """
    openai.api_key = api_key # Set the API key for this call

    prompt = f"""
    You are an expert business idea generator.
    Given the business domain: {business_domain}

    Generate an innovative business idea.
    Provide the following details for the idea:
    1. Business Name: A catchy and relevant name for the business.
    2. Business Description: A brief description of the business and its core concept.
    3. Tagline: A short, memorable tagline for the business.

    Please format your response as a JSON object with the keys "businessName", "businessDescription", and "tagline".
    For example:
    {{
      "businessName": "HealthSpark",
      "businessDescription": "An AI-powered platform that creates personalized fitness and nutrition plans based on genetic markers and lifestyle data.",
      "tagline": "Unlock Your Genetic Potential."
    }}
    """

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or another suitable model
            prompt=prompt,
            max_tokens=250, # Adjust as needed
            n=1,
            stop=None,
            temperature=0.7, # Adjust for creativity
        )

        generated_text = response.choices[0].text.strip()

        # Try to parse the response as JSON
        try:
            idea_details = json.loads(generated_text)
        except json.JSONDecodeError:
            # Fallback if the response is not perfect JSON (this is a common issue)
            # We'll try to extract the information using string searching or regex if needed.
            # For now, we'll print a warning and try a simple extraction.
            logging.warning(f"Could not parse OpenAI response as JSON. Raw response:\n{generated_text}")
            # Basic fallback (highly dependent on consistent non-JSON output format)
            idea_details = {}
            for line in generated_text.split('\n'):
                if "Business Name:" in line:
                    idea_details["businessName"] = line.split("Business Name:", 1)[1].strip()
                elif "Business Description:" in line:
                    idea_details["businessDescription"] = line.split("Business Description:", 1)[1].strip()
                elif "Tagline:" in line:
                    idea_details["tagline"] = line.split("Tagline:", 1)[1].strip()

            if not all(k in idea_details for k in ["businessName", "businessDescription", "tagline"]):
                logging.error("Fallback extraction failed to get all required fields.")
                return {
                    "businessName": "Error generating name",
                    "businessDescription": "Error generating description",
                    "tagline": "Error generating tagline"
                }


        # Ensure all keys are present, even if fallback was used
        final_idea = {
            "businessName": idea_details.get("businessName", "N/A"),
            "businessDescription": idea_details.get("businessDescription", "N/A"),
            "tagline": idea_details.get("tagline", "N/A")
        }
        return final_idea

    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return {
            "businessName": "Error generating name",
            "businessDescription": "Error generating description",
            "tagline": "Error generating tagline"
        }

def validate_idea(business_name: str, business_description: str, tagline: str, api_key: str) -> dict:
    """
    Validates the potential of the generated business idea using OpenAI.

    Args:
        business_name (str): The name of the business.
        business_description (str): The description of the business.
        tagline (str): The tagline of the business.
        api_key (str): The OpenAI API key.

    Returns:
        dict: A dictionary containing validation insights.
    """
    openai.api_key = api_key

    prompt = f"""
    You are an expert business analyst.
    Analyze the following business idea:

    Business Name: {business_name}
    Description: {business_description}
    Tagline: {tagline}

    Provide a concise validation of this business idea in 2-3 sentences.
    Consider its potential, possible challenges, and overall viability.
    For example:
    The idea for '{business_name}' shows promise due to its focus on a growing market trend. However, potential challenges include high competition and the need for significant initial investment in technology.
    """

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.6,
        )
        validation_summary = response.choices[0].text.strip()
        # Ensure the output is a dictionary as per return type hint
        return {"validation_summary": validation_summary}
    except Exception as e:
        logging.error(f"Error calling OpenAI API for validation: {e}")
        return {"validation_summary": "Error performing validation."}

def define_business_elements(business_name: str, business_description: str, api_key: str) -> dict:
    """
    Defines key business elements for the given idea using OpenAI.

    Args:
        business_name (str): The name of the business.
        business_description (str): The description of the business.
        api_key (str): The OpenAI API key.

    Returns:
        dict: A dictionary containing:
            - coreValueProposition (str)
            - primaryTargetAudience (str)
            - demographics (str)
            - uniqueSellingPoints (list[str])
            - initialRevenueModel (str)
    """
    openai.api_key = api_key

    prompt = f"""
    You are an expert business strategist.
    For the business idea:
    Name: {business_name}
    Description: {business_description}

    Define the following key business elements:
    1. Core Value Proposition: What is the main value offered to customers?
    2. Primary Target Audience: Who are the main customers?
    3. Demographics: Specific demographic details of the target audience (e.g., age, location, interests).
    4. Unique Selling Points (USPs): What makes this business different from competitors? List 2-3 key USPs.
    5. Initial Revenue Model: How will the business initially generate revenue?

    Please format your response as a JSON object with the keys:
    "coreValueProposition", "primaryTargetAudience", "demographics", "uniqueSellingPoints" (as a list of strings), and "initialRevenueModel".
    For example:
    {{
      "coreValueProposition": "Personalized wellness through AI-driven genetic analysis.",
      "primaryTargetAudience": "Health-conscious individuals seeking tailored fitness and nutrition advice.",
      "demographics": "Adults aged 25-55, urban and suburban areas, interested in technology and preventative health.",
      "uniqueSellingPoints": [
        "Hyper-personalized plans based on genetics.",
        "Adaptive AI that learns and adjusts with the user.",
        "Integration with wearable devices for seamless tracking."
      ],
      "initialRevenueModel": "Subscription-based access to personalized plans and premium features."
    }}
    """

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=400, # Increased max_tokens for more detailed output
            n=1,
            stop=None,
            temperature=0.7,
        )
        generated_text = response.choices[0].text.strip()

        try:
            elements = json.loads(generated_text)
        except json.JSONDecodeError:
            logging.warning(f"Could not parse OpenAI response for business elements as JSON. Raw response:\n{generated_text}")
            # Basic fallback - this would be very complex to make robust
            elements = {
                "coreValueProposition": "Error extracting - check raw output",
                "primaryTargetAudience": "Error extracting - check raw output",
                "demographics": "Error extracting - check raw output",
                "uniqueSellingPoints": ["Error extracting - check raw output"],
                "initialRevenueModel": "Error extracting - check raw output"
            }
            # A more sophisticated fallback would try to parse line by line based on keywords.

        # Ensure all keys are present
        default_elements = {
            "coreValueProposition": "N/A",
            "primaryTargetAudience": "N/A",
            "demographics": "N/A",
            "uniqueSellingPoints": [],
            "initialRevenueModel": "N/A"
        }
        for key, default_value in default_elements.items():
            if key not in elements:
                elements[key] = default_value
            if key == "uniqueSellingPoints" and not isinstance(elements[key], list):
                 elements[key] = [str(elements[key])]


        return elements

    except Exception as e:
        logging.error(f"Error calling OpenAI API for business elements: {e}")
        return {
            "coreValueProposition": "Error generating",
            "primaryTargetAudience": "Error generating",
            "demographics": "Error generating",
            "uniqueSellingPoints": ["Error generating"],
            "initialRevenueModel": "Error generating"
        }

def check_name_availability(business_name: str) -> dict:
    """
    Checks the availability of a business name, primarily by checking .com domain availability.

    Args:
        business_name (str): The name of the business.

    Returns:
        dict: A dictionary indicating domain availability.
              e.g., {"domain_name": "example.com", "status": "unavailable", "details": "Registered on ..."}
              or {"domain_name": "example.com", "status": "available"}
    """
    # Sanitize the business name to form a potential domain name
    # Remove spaces, special characters, and convert to lowercase
    # This is a basic sanitization, more sophisticated logic might be needed
    base_name = ''.join(filter(str.isalnum, business_name)).lower()
    if not base_name:
        return {
            "domain_name": "",
            "status": "invalid_name",
            "details": "Business name is empty or contains no alphanumeric characters."
        }

    domain_to_check = base_name + ".com" # Check .com by default

    try:
        domain_info = whois.whois(domain_to_check)
        if domain_info.status is None and not domain_info.expiration_date : # Often indicates availability
             # Sometimes no status and no expiration means it's available (depends on registrar/whois server)
             # Or if domain_info.text contains "No match for domain" or similar
            if domain_info.text and ("No match for domain" in domain_info.text or "NOT FOUND" in domain_info.text or "No Data Found" in domain_info.text or "is available for registration" in domain_info.text):
                 return {"domain_name": domain_to_check, "status": "available"}
            # If there's some data, it's likely registered, even if status is None
            # This part can be tricky as WHOIS responses vary a lot.
            return {"domain_name": domain_to_check, "status": "likely_unavailable", "details": "WHOIS data found but status is unclear. Manual check recommended."}

        # If domain_info.status is a list, check common "unavailable" statuses
        if isinstance(domain_info.status, list) and any(s in ' '.join(domain_info.status).lower() for s in ['ok', 'active', 'clienttransferprohibited']):
            return {"domain_name": domain_to_check, "status": "unavailable", "details": f"Registered on: {domain_info.creation_date}. Status: {domain_info.status}"}

        # If domain_info.status is a string
        if isinstance(domain_info.status, str) and any(s in domain_info.status.lower() for s in ['ok', 'active', 'clienttransferprohibited']):
             return {"domain_name": domain_to_check, "status": "unavailable", "details": f"Registered on: {domain_info.creation_date}. Status: {domain_info.status}"}


        # Default to available if no clear signs of unavailability, but this is risky
        # A more robust check would look for "No match" type strings in domain_info.text
        if domain_info.text and ("No match for domain" in domain_info.text or "NOT FOUND" in domain_info.text or "No Data Found" in domain_info.text or "is available for registration" in domain_info.text):
            return {"domain_name": domain_to_check, "status": "available"}

        # Fallback for unclear cases
        return {"domain_name": domain_to_check, "status": "unknown", "details": "WHOIS response was inconclusive. Manual check recommended."}

    except whois.parser.PywhoisError as e:
        # This often means the domain is not registered / does not exist
        if "No match for domain" in str(e) or "No whois server is known for domain" in str(e) :
             return {"domain_name": domain_to_check, "status": "available", "details": str(e)}
        return {"domain_name": domain_to_check, "status": "error_checking", "details": str(e)}
    except Exception as e: # Catch any other unexpected errors
        logging.error(f"Error checking domain availability for {domain_to_check}: {e}")
        return {"domain_name": domain_to_check, "status": "error_checking", "details": str(e)}

def run_business_idea_pipeline(business_domain: str, api_key: str, max_name_checks: int = 3) -> dict:
    """
    Orchestrates the pipeline of generating, validating, defining, and checking a business idea.

    Args:
        business_domain (str): The business domain.
        api_key (str): The OpenAI API key.
        max_name_checks (int): Maximum attempts to find an available name.

    Returns:
        dict: A dictionary containing the full business idea details.
    """

    idea_elements = None
    business_name = None
    name_check_result = None

    for attempt in range(max_name_checks):
        logging.info(f"--- Attempt {attempt + 1} of {max_name_checks} for Name Generation & Check ---")

        current_domain_prompt = business_domain
        if attempt > 0 and business_name: # If retrying, ask for a different name
            current_domain_prompt = f"{business_domain} (previously tried '{business_name}', please suggest a different business name)"

        # Step 1: Idea Generation
        logging.info("--- Step 1: Idea Generation ---")
        idea_elements = generate_idea(current_domain_prompt, api_key)
        logging.debug(json.dumps(idea_elements, indent=2)) # Changed to debug

        if not idea_elements or idea_elements.get("businessName") == "Error generating name" or not idea_elements.get("businessName"):
            logging.error("Error in idea generation. Cannot proceed.")
            return {"error": "Idea generation failed."}

        business_name = idea_elements["businessName"]
        business_description = idea_elements["businessDescription"]
        tagline = idea_elements["tagline"]

        # Step 4 (run earlier for retry logic): Name Availability Check
        logging.info("--- Step 4: Name Availability Check ---")
        name_check_result = check_name_availability(business_name)
        logging.debug(json.dumps(name_check_result, indent=2)) # Changed to debug

        if name_check_result.get("status") == "available":
            logging.info(f"Business name '{business_name}' appears to be available.")
            break # Name is available, exit loop
        elif name_check_result.get("status") == "error_checking" or name_check_result.get("status") == "invalid_name":
             logging.warning(f"Could not reliably check name '{business_name}'. Stopping name search.")
             break # Error in checking, stop trying
        else:
            logging.warning(f"Business name '{business_name}' is likely unavailable or status is unknown.")
            if attempt == max_name_checks - 1:
                logging.warning("Maximum name check attempts reached. Proceeding with the last generated name.")

    if not idea_elements or not business_name: # Should not happen if generation worked once
        return {"error": "Failed to generate a business name after multiple attempts."}

    # Proceed with other steps using the latest 'business_name', 'business_description', 'tagline'
    # and 'name_check_result'.

    # Step 2: Idea Validation
    logging.info("--- Step 2: Idea Validation ---")
    validation_result = validate_idea(business_name, business_description, tagline, api_key)
    logging.debug(json.dumps(validation_result, indent=2)) # Changed to debug

    # Step 3: Defining Business Elements
    logging.info("--- Step 3: Defining Business Elements ---")
    business_details = define_business_elements(business_name, business_description, api_key)
    logging.debug(json.dumps(business_details, indent=2)) # Changed to debug

    # Combine all results for the final expected output format
    final_output = {
        "businessName": business_name,
        "BusinessDescription": business_description, # Per user's original example
        "tagline": tagline,
        "coreValueProposition": business_details.get("coreValueProposition"),
        "primaryTargetAudience": business_details.get("primaryTargetAudience"),
        "demographics": business_details.get("demographics"),
        "uniqueSellingPoints": business_details.get("uniqueSellingPoints"),
        "initialRevenueModel": business_details.get("initialRevenueModel"),
        "validationSummary": validation_result.get("validation_summary"),
        "nameAvailability": name_check_result
    }
    logging.info("--- Final Combined Output ---")
    print(json.dumps(final_output, indent=2)) # Keep final output as print or change to logging.info if preferred
    return final_output

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Generate and analyze a business idea.")
    parser.add_argument("domain", type=str, help="The business domain (e.g., 'health and fitness using AI')")
    parser.add_argument("--api_key", type=str, default=os.getenv("OPENAI_API_KEY"), help="OpenAI API Key. Defaults to OPENAI_API_KEY env variable.")
    parser.add_argument("--max_retries", type=int, default=3, help="Maximum retries for finding an available business name.")

    args = parser.parse_args()

    if not args.api_key:
        logging.error("OpenAI API Key is required. Set the OPENAI_API_KEY environment variable or use the --api_key argument.")
    elif not args.domain:
        logging.error("Business domain is required.")
    else:
        logging.info(f"Starting business idea pipeline for domain: '{args.domain}'")
        pipeline_result = run_business_idea_pipeline(args.domain, args.api_key, args.max_retries)

        # Optionally, save the result to a file
        # output_filename = "business_idea_output.json"
        # with open(output_filename, 'w') as f:
        #     json.dump(pipeline_result, f, indent=2)
        # print(f"\nFull output saved to {output_filename}")
