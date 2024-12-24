from flask import Flask, render_template, request, jsonify
import json
import os

# Global variable to track the current index
current_index = 0

# File path for the JSON data
DATA_FILE_PATH = 'data.json'
SELECTIONS_FILE_PATH = 'selections.json'
app = Flask(__name__)

@app.route('/')
def index():
    global current_index

    # Load your JSON data
    with open(DATA_FILE_PATH, 'r') as file:
        data = json.load(file)

    # Load the selections data
    if os.path.exists(SELECTIONS_FILE_PATH):
        with open(SELECTIONS_FILE_PATH, 'r') as file:
            selections = json.load(file)
    else:
        selections = []

    # Get SKUs from selections
    processed_skus = {item['SKU'] for item in selections}

    # Filter data to exclude already selected SKUs
    filtered_data = [item for item in data if item['SKU'] not in processed_skus]

    # Check if there are any products left to display
    if not filtered_data:
        return render_template('index.html', message="All products were added to the catalog", items=[])

    # Reset the index if out of range
    if current_index >= len(filtered_data):
        current_index = 0

    # Display the current item
    return render_template('index.html', items=[filtered_data[current_index]])

@app.route('/submit', methods=['POST'])
def submit():
    global current_index

    # File path for the JSON file
    json_file_path = SELECTIONS_FILE_PATH

    # Initialize the list for final output
    final_data = []

    # Get all submitted data
    selections = request.form.getlist('item_checks')
    other_category = request.form.get('other_category')  # Retrieve the text entered in the "Other Category" field
    product_name = request.form.get('product_name') 
    
    # Retrieving prices for each size
    price_xs = request.form.get('price_xs')
    price_s = request.form.get('price_s')
    price_m = request.form.get('price_m')
    price_l = request.form.get('price_l')
    price_xl = request.form.get('price_xl')
    price_2xl = request.form.get('price_2xl')
    price_3xl = request.form.get('price_3xl')
    price_4xl = request.form.get('price_4xl')
    price_5xl = request.form.get('price_5xl')
    price_6xl = request.form.get('price_6xl')
    price_other = request.form.get('price_other')
    print("Submitted Selections:", selections)

    # Extract SKU
    sku = next((item for item in selections if not item.startswith("Gender") and not " > " in item), None)

    # Extract Gender
    gender = next((item for item in selections if item.startswith("Gender")), None)

    # Extract Categories
    categories = [item for item in selections if " > " in item and not item.startswith("Gender")]


    if other_category and other_category.strip():  # Ensure it's not empty or just whitespace
        categories.append(f"Other Category > {other_category.strip()}")



    # Build the JSON structure for this submission
    result = {
        "SKU": sku,
        "Category": categories,
        "Gender": gender,
        "Manual_name": product_name,
        "Prices": {  # Using a dictionary instead of a list to store key-value pairs
            "XS": price_xs,
            "S": price_s,
            "M": price_m,
            "L": price_l,
            "XL": price_xl,
            "2XL": price_2xl,
            "3XL": price_3xl,
            "4XL": price_4xl,
            "5XL": price_5xl,
            "6XL": price_6xl,
            "Other": price_other
        }
    }


    # Load existing data from the JSON file
    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                existing_data = json.load(file)
        else:
            existing_data = []
    except json.JSONDecodeError:
        print("Invalid or empty JSON file detected. Initializing with an empty list.")
        existing_data = []

    # Append the new structured data
    existing_data.append(result)

    # Save the updated data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

    # Load your JSON data
    with open(DATA_FILE_PATH, 'r') as file:
        data = json.load(file)

    # Load the selections data
    if os.path.exists(SELECTIONS_FILE_PATH):
        with open(SELECTIONS_FILE_PATH, 'r') as file:
            selections_data = json.load(file)
    else:
        selections_data = []

    # Filter data to exclude already selected SKUs
    processed_skus = {item['SKU'] for item in selections_data}
    filtered_data = [item for item in data if item['SKU'] not in processed_skus]

    # Increment the counter
    current_index += 1

    # Reset the index if it exceeds the filtered_data length
    if current_index >= len(filtered_data):
        current_index = 0

    # Check if all products are processed
    if not filtered_data:
        return render_template('index.html', message="All products were added to the catalog", items=[])

    # Display the next item
    return render_template('index.html', items=[filtered_data[current_index]])

if __name__ == '__main__':
    app.run(debug=True)
