# Env Setup

### Python 3.13.7 via pyenv
```
cd ~/secure-agent-execution
mkdir privacy-hr-pipeline
cd privacy-hr-pipeline
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy faker jupyter matplotlib
```
```faker``` generates realistic fake names/data, 

```pandas/numpy``` for the data manipulation, 

```matplotlib``` for visualizing later,

 ```jupyter``` lets us work interactively if we prefer notebooks for exploration before turning things into clean scripts.


## ```.gitignore```: Keep venv/ folder out of the repo
```
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.csv" >> .gitignore
```

## ```requirements.txt```: Reproducable setup

```
pip freeze > requirements.txt
git add .gitignore requirements.txt
```

To recreate the environment: ```pip install -r requirements.txt```
### Notes: 

- Press Cmd + Shift + P to open the Command Palette.Type Python: Select Interpreter and select it.Look for the entry that says ('venv': venv) or shows the path containing privacy-hr-pipeline/venv/bin/python. Click it.

- Repo name changed, venv connection not available at the repo level
  ```
  cd ai-security-portfolio/privacy-hr-pipeline
  deactivate
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install pandas numpy faker jupyter matplotlib
  jupyter notebook

  ```
  otherwise
  ```
  python3 -m venv venv
  source venv/bin/activate
  jupyter notebook

  ```
- For the dashboard install streamlit
    
  ```
  source venv/bin/activate
  pip install streamlit
  ```
