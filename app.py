from flask import Flask, render_template, request
import os
import yaml
import joblib
import pandas as pd
import logging
import inflect
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file")
genai.configure(api_key=API_KEY)

# Setup logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Paths
params_path = 'params.yaml'
webapp_root = 'webapp'
static_dir = os.path.join(webapp_root, 'static')
template_dir = os.path.join(webapp_root, 'templates')

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

# Read YAML config
def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

# Prediction function
def predict(data: pd.DataFrame):
    try:
        config = read_params(params_path)
        model_dir_path = config["webapp_model_dir"]
        model = joblib.load(model_dir_path)

        # Ensure correct columns
        expected_cols = model.feature_names_in_
        for col in expected_cols:
            if col not in data.columns:
                data[col] = 0
        data = data[expected_cols]

        prediction = model.predict(data)
        return prediction
    except Exception as e:
        logging.error(f"Prediction error: {e}", exc_info=True)
        return None


# Fallback advice generation
def generate_fallback_advice(age, sex, bmi, children, smoker, region, predicted_cost):
    advice_parts = []

    # Age-based advice
    if age < 30:
        advice_parts.append("As a younger adult, you may benefit from high-deductible plans with lower premiums.")
    elif age > 50:
        advice_parts.append("Consider comprehensive plans that cover preventive care and chronic conditions.")

    # BMI-based advice
    if bmi > 30:
        advice_parts.append("Maintaining a healthy weight can significantly reduce your insurance costs over time.")
    elif bmi < 25:
        advice_parts.append("Your healthy BMI puts you in a lower risk category for many insurers.")

    # Smoker advice
    if smoker == 1:
        advice_parts.append("Quitting smoking could reduce your premiums by up to 50% after a few years.")
    else:
        advice_parts.append("As a non-smoker, you're already in a lower premium bracket.")

    # Children advice
    if children > 2:
        advice_parts.append("Families with multiple children should look for family plans with good pediatric coverage.")

    # Cost-based advice
    cost_float = float(predicted_cost)
    if cost_float > 10000:
        advice_parts.append("Your predicted premium is above average. Consider shopping around for quotes from multiple insurers.")
    elif cost_float < 5000:
        advice_parts.append("Your predicted premium is below average - great job maintaining healthy lifestyle factors!")

    # General advice
    advice_parts.append("Remember to review your policy annually and consider your changing healthcare needs.")

    return " ".join(advice_parts[:3])  # Return up to 3 pieces of advice

# Gemini text generation
def generate_text(prompt: str, retries=2) -> str:
    for i in range(retries + 1):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logging.warning(f"GenAI attempt {i+1} failed: {e}")
            if i < retries:  # Don't sleep on the last attempt
                import time
                time.sleep(1)  # Brief pause between retries

    # If AI fails, provide fallback advice
    logging.info("Using fallback advice generation")
    return "AI advice is currently unavailable. Here's some general guidance: " + generate_fallback_advice(
        age=int(prompt.split('Age: ')[1].split('\n')[0]),
        sex=0 if 'Female' in prompt else 1,
        bmi=float(prompt.split('BMI: ')[1].split('\n')[0]),
        children=int(prompt.split('Children: ')[1].split('\n')[0]),
        smoker=0 if 'Smoker: No' in prompt else 1,
        region=prompt.split('Region: ')[1].split('\n')[0],
        predicted_cost=prompt.split('Predicted Insurance Cost: $')[1].split('.')[0]
    )

# Flask route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Validate and parse input
            try:
                age = int(request.form.get("age"))
                bmi = float(request.form.get("bmi"))
                children = int(request.form.get("children"))
            except ValueError:
                return render_template("error.html", error={"error": "Please enter valid numeric values."})

            sex = 0 if request.form.get("sex") == "female" else 1
            smoker = 0 if request.form.get("smoker") == "no" else 1
            region_map = {"SouthWest": 0, "SouthEast": 1, "NorthWest": 2, "NorthEast": 3}
            region = region_map.get(request.form.get("region"), 0)

            # Predict insurance cost
            input_df = pd.DataFrame([[age, sex, bmi, children, smoker, region]],
                                    columns=['age','sex','bmi','children','smoker','region'])
            response = predict(input_df)
            if response is None:
                return render_template("error.html", error={"error": "Prediction failed"})

            final_val = "{:.2f}".format(response[0])
            final_ans = inflect.engine().number_to_words(final_val)

            # Generate AI advice
            ai_prompt = f"""
Predicted Insurance Cost: ${final_val}.
User Details:
- Age: {age}
- Sex: {'Female' if sex==0 else 'Male'}
- BMI: {bmi}
- Children: {children}
- Smoker: {'No' if smoker==0 else 'Yes'}
- Region: {request.form.get('region')}

Generate a concise advice or explanation for this user.
"""
            ai_response = generate_text(ai_prompt)

            return render_template("home.html",
                                   response_int=final_val,
                                   response=str(final_ans),
                                   ai_response=ai_response)
        except Exception as e:
            logging.error(f"Form processing error: {e}", exc_info=True)
            return render_template("error.html", error={"error": str(e)})

    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
