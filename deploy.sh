#!/bin/bash

# CoverCast AI Deployment Helper Script
# This script helps prepare your app for deployment

echo "🚀 CoverCast AI Deployment Preparation"
echo "======================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Gemini API key"
    echo "   API_KEY=your_actual_gemini_api_key_here"
else
    echo "✅ .env file exists"
fi

# Check if model file exists
if [ ! -f "saved_models/model_pipeline.joblib" ]; then
    echo "❌ Model file not found at saved_models/model_pipeline.joblib"
    echo "   Please ensure your trained model is in the correct location"
    exit 1
else
    echo "✅ Model file found"
fi

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
else
    echo "✅ requirements.txt found"
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Render (Recommended): https://render.com"
echo "2. Railway: https://railway.app"
echo "3. PythonAnywhere: https://www.pythonanywhere.com"
echo "4. Vercel: https://vercel.com"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "🔧 Quick steps for Render:"
echo "   1. Push code to GitHub"
echo "   2. Sign up at render.com"
echo "   3. Connect GitHub repository"
echo "   4. Add API_KEY environment variable"
echo "   5. Deploy! 🎉"
