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


# Gemini chat generation
def generate_text(prompt: str, retries=1) -> str:
    for i in range(retries + 1):
        try:
            model = genai.get_model("gemini-2.5-t")
            response = model.chat([{"role": "user", "content": prompt}])
            if response.last:
                return str(response.last)
        except Exception as e:
            logging.warning(f"GenAI attempt {i+1} failed: {e}")
    return "Sorry, could not generate advice."

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
    app.run(host="0.0.0.0", port=5000, debug=True)
