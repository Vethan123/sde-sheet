from flask import Flask, request, render_template, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Load the datasets
file_path = 'Modified_Leetcode_Questions_Split.csv'
data = pd.read_csv(file_path)

# Define the desired order and emojis for the headings
CATEGORY_ORDER = {
    "Easy": "\U0001F7E2",
    "Tricky": "\U0001F914",
    "Edge Case Intensive": "\U0001F522",
    "Optimization Required": "\u26A1",
    "Hard": "\U0001F534",
    "MultiConcept": "\U0001F517"
}

# Define difficulty mapping for each skill level
DIFFICULTY_LEVELS = {
    "beginner": ["Easy", "Tricky"],
    "intermediate": ["Tricky", "Optimization Required", "Edge Case Intensive"],
    "advanced": ["Hard", "Optimization Required", "MultiConcept"]
}


# Function to determine difficulty dynamically
def determine_difficulty(tags, levels):
    for level, tags_list in levels.items():
        for tag in tags_list:
            if tag in tags:
                return level
    return None


# Add a Difficulty column dynamically based on the Tags
data['Difficulty'] = data['Tags'].apply(lambda x: determine_difficulty(str(x), DIFFICULTY_LEVELS))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the form inputs
        num_questions = int(request.form.get('num_questions', 30))
        category = request.form.get('category')
        level = request.form.get('level')  # Get the selected skill level
        return redirect(url_for('display_questions', num_questions=num_questions, category=category, level=level))

    # Render the form for user input, passing the possible categories for each skill level
    return render_template('index.html', category_order=CATEGORY_ORDER)


@app.route('/questions/<int:num_questions>/<category>/<level>')
def display_questions(num_questions, category, level):
    # Ensure Acceptance is numeric
    data['Acceptance'] = data['Acceptance'].astype(str).str.rstrip('%').astype(float)

    # Sort by Acceptance rate
    data_sorted = data.sort_values(by=['Acceptance'], ascending=False)

    # Filter by category
    filtered_data = data_sorted[data_sorted['Tags'].str.contains(category, na=False)]

    # Filter by difficulty level
    selected_difficulties = DIFFICULTY_LEVELS.get(level, [])
    filtered_data = filtered_data[filtered_data['Tags'].apply(lambda x: any(tag in x for tag in selected_difficulties))]

    # Get the top `num_questions`
    filtered_questions = filtered_data.head(num_questions)

    return render_template(
        'questions.html',
        filtered_questions=filtered_questions,
        num_questions=num_questions,
        category=category,
        level = level,
        category_order=CATEGORY_ORDER
    )


if __name__ == "__main__":
    app.run(debug=True)


