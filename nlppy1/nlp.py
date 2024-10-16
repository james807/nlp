from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import openai  # Correct import for OpenAI API

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your OpenAI API key from environment variable or set it directly (not recommended for production)
openai.api_key = os.getenv("sk-O2DXLFWl0Rni51DT9wQaVhJGlM5GrBt2jBYSowW1AsT3BlbkFJnuaFnaViuJajhdIeMcc5m0w0sXNleXpKbzIDLMzeQA")  # Set your OpenAI API key here

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def process_summary_data(df):
    numerical_df = df.select_dtypes(include=['number'])
    datetime_df = df.select_dtypes(include=['datetime'])

    summary = numerical_df.describe().transpose()

    summary['mean'] = summary['mean'].astype(float).tolist()
    summary['min'] = summary['min'].astype(float).tolist()
    summary['25%'] = summary['25%'].astype(float).tolist()
    summary['50%'] = summary['50%'].astype(float).tolist()
    summary['75%'] = summary['75%'].astype(float).tolist()
    summary['max'] = summary['max'].astype(float).tolist()
    summary['std'] = summary['std'].astype(float).tolist()
    summary['count'] = summary['count'].astype(float).tolist()

    labels = summary.index.tolist()
    means = summary['mean'].tolist()

    datetime_summary = {}
    if not datetime_df.empty:
        datetime_summary = {
            'count': len(datetime_df),
            'first': datetime_df.min().to_list(),
            'last': datetime_df.max().to_list()
        }

    return {
        'labels': labels,
        'unitPrices': means,
        'summaryStats': {
            'mean': means,
        },
        'datetimeSummary': datetime_summary
    }

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file.filename.endswith('.txt'):
            df = pd.read_csv(file_path, delimiter='\t')
        else:
            return jsonify({'error': 'Unsupported file type.'})

        summary = process_summary_data(df)
        data_table_html = df.to_html(classes='table table-striped', index=False)

        return jsonify({'table': data_table_html, 'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/query', methods=['POST'])
def query_data():
    data = request.json
    query = data.get('query')
    file_name = data.get('file')

    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

        if query == "summary":
            summary = process_summary_data(df)
            return jsonify({'result': 'Summary statistics generated.', 'summaryData': summary})

        # Prepare context with data for OpenAI API
        context = df.to_csv(index=False)
        prompt = f"Using the following data, please answer the query: {query}\n\nData:\n{context}"

        # Call OpenAI API
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # Return the response from OpenAI
        return jsonify({'result': completion['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
