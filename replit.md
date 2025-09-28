# Mlangizi wa Ulimi - Agricultural Advisor Bot

## Overview

This is a comprehensive AI-powered agricultural advisory system designed specifically for Malawi farmers, built as a Telegram bot. The system provides weather-integrated crop recommendations, variety information, historical rainfall analysis, and intelligent farming guidance using machine learning and natural language processing. The bot integrates real weather data, agricultural knowledge bases, and AI-powered analysis to deliver personalized farming advice through an accessible Telegram interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
The system follows a modular microservices-like architecture with clear separation of concerns:

**Bot Framework**: Built on python-telegram-bot 20.7 for handling Telegram interactions, with asynchronous message processing and callback query support for interactive features.

**Weather Integration**: Multi-layered weather system using OpenWeatherMap API for current conditions and forecasts, with a specialized historical weather analyzer that processes 5-year rainfall patterns to provide climate trend analysis and drought/flood risk assessment.

**AI Enhancement Layer**: Integrated OpenAI GPT-3.5-turbo for intelligent response synthesis, recommendation enhancement, and natural language processing of user queries. The AI layer provides contextual insights and improves recommendation quality through prompt engineering.

**Knowledge Management**: Sophisticated document processing pipeline that ingests agricultural PDFs, processes them through text chunking algorithms, generates embeddings via OpenAI's text-embedding-ada-002 model, and stores them in a SQLite vector database for semantic search capabilities.

**Recommendation Engine**: Multi-factor crop recommendation system that analyzes 10+ variables including rainfall patterns, temperature, humidity, soil conditions, historical data, climate trends, and seasonal timing to generate scored crop recommendations with confidence levels.

### Database Design
**Primary Storage**: SQLite vector database for document embeddings and semantic search, designed for zero-setup deployment while maintaining production-grade performance.

**Vector Operations**: Custom implementation of cosine similarity search for document retrieval, with JSON-stored embeddings and efficient indexing strategies.

**Data Models**: Structured JSON storage for crop varieties, weather cache, user analytics, and feedback systems with clear schemas for agricultural data.

### API Integration Strategy
**Weather Services**: OpenWeatherMap API integration with intelligent caching, rate limiting, and fallback mechanisms for reliable weather data access.

**AI Services**: OpenAI API integration with proper error handling, token optimization, and response caching to minimize costs while maximizing response quality.

**Geolocation**: Coordinate handling system that processes both GPS coordinates and location names with validation and geocoding capabilities.

### Processing Pipelines
**Document Processing**: Automated PDF ingestion pipeline that extracts text, chunks content intelligently, generates embeddings, and indexes documents for search with quality scoring and validation.

**Weather Analysis**: Historical weather data processing that calculates trends, variability measures, seasonal patterns, and risk assessments from multi-year datasets.

**Recommendation Generation**: Complex scoring algorithm that weighs multiple agricultural factors, applies historical data insights, and generates confidence-scored recommendations with explanatory context.

## External Dependencies

### APIs and Services
- **OpenAI API**: Text embeddings (text-embedding-ada-002) for semantic search and GPT-3.5-turbo for AI-powered recommendations and response enhancement
- **OpenWeatherMap API**: Current weather conditions, 7-day forecasts, and historical weather data for comprehensive meteorological analysis
- **Telegram Bot API**: Core bot functionality including message handling, inline keyboards, callback queries, and user interaction management

### Python Dependencies
- **python-telegram-bot 20.7**: Telegram bot framework with async support
- **openai**: Official OpenAI Python client for embeddings and chat completions
- **requests**: HTTP client for weather API calls and external service integration
- **python-dotenv**: Environment variable management for secure configuration
- **numpy**: Numerical operations for vector calculations and similarity search
- **pandas**: Data analysis and processing for weather and agricultural data
- **PyPDF2**: PDF text extraction for knowledge base document processing
- **faiss-cpu**: Vector similarity search library (fallback option)
- **sqlite3**: Built-in database for vector storage and application data

### Infrastructure Requirements
- **File System Storage**: Local storage for PDF documents, vector databases, configuration files, and cache data
- **Environment Variables**: Secure configuration management for API keys and sensitive settings
- **Network Access**: Required for API calls to OpenAI, OpenWeatherMap, and Telegram services
- **Python 3.8+**: Runtime environment with async/await support for concurrent operations

### Development and Testing Tools
- **pytest**: Comprehensive testing framework with fixtures for unit and integration tests
- **unittest.mock**: Mocking framework for testing API integrations and external dependencies
- **Flask/Flask-CORS**: Optional web API server for frontend integration and cross-origin support
- **asyncio**: Asynchronous programming support for handling concurrent bot operations