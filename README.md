# ResQHer — Complete Deploy Guide

## Step 1 — Edit ONE line in index.html AND dashboard.html
Open each file in Notepad. Find this line:
   const API = 'https://YOUR_USERNAME.pythonanywhere.com';
Replace YOUR_USERNAME with your actual PythonAnywhere username.

## Step 2 — Upload to PythonAnywhere (backend)
Files to upload: app.py, requirements.txt
Console command: pip3 install flask flask-cors werkzeug --user
WSGI file content:
   import sys
   sys.path.insert(0, '/home/YOURUSERNAME')
   from app import app as application

## Step 3 — Upload to GitHub (frontend)
Files to upload: index.html, dashboard.html, style.css, vercel.json, logo.png, README.md
Go to github.com → New repo named "resqher" → Public → upload all files

## Step 4 — Deploy on Vercel
Go to vercel.com → Add New Project → import "resqher" repo
Framework: Other (NOT Vite)
Build Command: (leave blank)
Output Directory: (leave blank)
Click Deploy → your app is live!

## Your live URL will be:
https://resqher.vercel.app  (or similar)
