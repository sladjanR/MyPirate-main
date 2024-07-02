from flask import Flask, render_template, jsonify
import json
from functools import reduce
import os

app = Flask("RISTOSLAKI")

#Function to read scores from the JSON file
def readscores():
    currentdir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(currentdir,'scores.json')
    with open(data_file, 'r') as f:
        return json.load(f)

#Map function: Add a certain value to all scores
def mapscores(scores, addvalue):
    return [{"player": s["player"], "score": s["score"] + addvalue} for s in scores]

#Reduce function: Sum of all scores
def reduce_scores(scores):
    return reduce(lambda x, y: x + y["score"], scores, 0)

#Filter function: Get scores above a certain value
def filter_scores(scores, threshold):
    return [s for s in scores if s["score"] > threshold]

@app.route('/')
def home():
    return "Welcome to the Game!"

@app.route('/scoreboard')
def scoreboard():
    scores = readscores()
    
    mappedS =  mapscores(scores, 0) #TODO Menjaj 0 u zavisnosti od broja koji dodaje
    mappedS = sorted(mappedS, key=lambda x: x["score"], reverse=True)

    
    filterS = filter_scores(scores, 100) # Preko 100 se racunaju
    filterS = sorted(filterS, key=lambda x: x["score"], reverse=True)
    total_score = reduce_scores(scores)
    summedS = [{"score": total_score}]
    sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    # print("Current directory: ", os.getcwd())  # Dodajte ovu liniju
    return render_template('scoreboard.html',mappedS = mappedS, filterS = filterS ,scores=sorted_scores, summedS = summedS)

@app.route('/api/scores')
def api_scores():
    scores = readscores()
    return jsonify(scores)

@app.route('/api/scores/mapped/<int:add_value>')
def api_scores_mapped(add_value):
    scores = readscores()
    mapped_scores = mapscores(scores, add_value)
    return jsonify(mapped_scores)

@app.route('/api/scores/reduced')
def api_scores_reduced():
    scores = readscores()
    total_score = reduce_scores(scores)
    return jsonify({"total_score": total_score})

@app.route('/api/scores/filtered/<int:threshold>')
def api_scores_filtered(threshold):
    scores = readscores()
    filtered_scores = filter_scores(scores, threshold)
    return jsonify(filtered_scores)

# if __name__ == '__main__':
#     app.run(debug=True)