import json
import os

from flask import Flask, redirect, render_template, url_for

from scheduler.solver import generate_schedule

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-solver")
def run_solver_route():
    generate_schedule()
    return redirect(url_for("view_results"))


@app.route("/results")
def view_results():
    output_path = os.path.join("output", "assignments.json")
    if os.path.exists(output_path):
        with open(output_path) as f:
            assignments = json.load(f)
    else:
        assignments = {}
    return render_template("results.html", assignments=assignments)


if __name__ == "__main__":
    app.run(debug=True)
