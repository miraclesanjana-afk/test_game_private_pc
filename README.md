# Word Scramble

A small interactive word-scramble game written in Python. Play it in a terminal,
guess the scrambled words, and earn points.

## Run the game

From the project folder, activate the virtual environment and start the game:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Each game has 10 rounds. Type the answer to score 10 points, type `hint` to get
a clue and score 5 points, type `skip` to reveal the word, or type `quit` to end
early.

## Run the Streamlit app

Install the project dependencies and launch the browser-based version:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app
   from that repository and select `app.py` as the main file.
3. Deploy. Streamlit Cloud installs the packages listed in `requirements.txt`.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Push to GitHub

Install Git for Windows and create an empty repository on GitHub. Then, from
this folder, run the following commands, replacing the URL with your repository
URL:

```powershell
git init
git add .gitignore app.py main.py requirements.txt tests\test_app.py tests\test_game.py README.md
git commit -m "Create interactive word scramble game"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
