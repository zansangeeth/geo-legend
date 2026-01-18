# Deploying Geo-Legend to Streamlit Cloud 🚀

## 1. Prepare Your Repository
Ensure you have the following files in your GitHub repository:
- `map_app.py` (The main application)
- `requirements.txt` (List of Python dependencies)
- `Median age of population (2023).csv` (Your data file)

## 2. Push to GitHub
If you haven't pushed your changes yet, run these commands in your terminal:

```sh
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Ready for deployment"

# Rename branch to main (if needed)
git branch -M main

# Add your remote repository (replace YOUR_GITHUB_USER and REPO_NAME)
# If you haven't created a repo on GitHub yet, go to https://github.com/new and create one first!
git remote add origin https://github.com/YOUR_GITHUB_USER/REPO_NAME.git

# Push to GitHub
git push -u origin main
```

## 3. Deploy on Streamlit Cloud
1. Go to [Streamlit Cloud](https://streamlit.io/cloud).
2. Sign in with GitHub.
3. Click **"New app"**.
4. Select your repository (`geo-legend`), branch (`main`), and main file (`map_app.py`).
5. Click **"Deploy!"**.

## Troubleshooting
- If the map doesn't show up, check the logs on the dashboard.
- If dependency errors occur, ensure `requirements.txt` is correct. `geopandas` installation on Cloud is usually smooth, but if it fails, check the logs for suggested binary package installs.
