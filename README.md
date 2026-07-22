# 🚚 Rig Log Spotter ELD

Welcome to Rig Log! This is a complete full stack application designed specifically for property carrying truck drivers. It allows dispatchers and drivers to enter a trip's current location, pickup point, dropoff point, and current cycle hours used. The system instantly calculates a compliant route map and auto generates FMCSA daily log sheets that strictly adhere to the 70 hour / 8 day Hours of Service (HOS) ruleset.

This project was built for the Spotter AI Full Stack Developer Assessment.

## 🛠️ Technology Stack

**Backend Architecture**
The backend is powered by Django 6 and the Django REST Framework. It handles all the heavy lifting for compliance calculations. For routing and geocoding, it integrates directly with OSRM and OpenStreetMap Nominatim, providing highly accurate mapping data without the need for expensive API keys.

**Frontend Interface**
The user interface is built with React and Vite for lightning fast performance. It features a modern, premium design utilizing glassmorphism and smooth animations. The map is rendered using Leaflet, while the daily log sheet grids are intricately drawn using custom SVG logic to perfectly mimic real FMCSA forms.

**Database Infrastructure**
For local development, the application uses a lightweight SQLite database. In production, it scales up to a robust PostgreSQL database connected via standard database URLs.

## 🚀 How The Engine Works

When a user submits a trip request, the frontend sends the data securely to the backend API.

The backend immediately geocodes all three locations using Nominatim. It then queries OSRM for two distinct route legs: the drive from the current location to the pickup, and the drive from the pickup to the final dropoff.

The core of the application lives in the HOS Engine. This complex simulation walks through the trip hour by hour and enforces the strict FMCSA ruleset. It monitors the 11 hour daily driving limit, the 14 hour on duty window, and forces a mandatory 30 minute break after 8 hours of continuous driving. It also tracks 10 hour resets, calculates the 34 hour restart at the 70 hour cycle limit, and injects mandatory fuel stops every 1,000 miles. Finally, it accounts for one hour of on duty time at both the pickup and dropoff locations. 

Once the simulation completes, the Log Builder takes that continuous timeline and slices it perfectly at midnight for every calendar day. This ensures that multi day trips are separated onto their own individual daily log sheets.

The frontend receives this processed data, plots the exact route coordinates on the Leaflet map, and visually draws the blue status lines across the SVG log sheet grids.

You can verify the accuracy of the HOS engine by running the comprehensive unit tests included in the repository. These tests cover everything from forced breaks and resets to fuel stops and midnight crossing logic.

## 💻 Local Development Guide

**Setting up the Backend**

First, navigate into the backend directory and set up your Python virtual environment. Install the required dependencies and run the initial database migrations. Once complete, you can start the Django development server on localhost port 8000. 

To run the unit tests, simply execute the manage.py test command targeting the trips app.

**Setting up the Frontend**

Navigate into the frontend directory and run npm install to pull down the React dependencies. Copy the example environment variables to point the frontend to your local Django server, and then start the Vite development server on port 5173.

## 🌐 Deployment Architecture

The backend is fully configured to deploy seamlessly to platforms like Railway or Render. By connecting your GitHub repository, Railway will automatically detect the Python environment, provision a PostgreSQL database, and run the necessary database migrations during the release phase.

The frontend is optimized for Vercel. Simply import the repository, and Vercel will automatically configure the Vite build settings. Once deployed, just ensure your backend allows Cross Origin Resource Sharing (CORS) requests from your new Vercel domain.

## 📋 Assessment Assumptions

Based on the assessment specifications, this engine assumes a property carrying driver operating under a standard 70 hour / 8 day cycle with no adverse driving conditions. It mandates fueling stops every 1000 miles and logs exactly one hour of on duty, non driving time for both pickups and dropoffs.
