# Project Brief: Azure Search RAG Assistant

## Overview
This project is a Flask-based Retrieval-Augmented Generation (RAG) application that leverages Azure OpenAI and Azure Search to provide AI-powered responses to user queries. The system retrieves relevant information from a knowledge base and uses it to generate contextually appropriate answers, complete with citations to the source material.

## Core Functionality
- User query processing through a web interface
- Vector search against an Azure Search index
- Context-aware response generation using Azure OpenAI
- Citation management for referencing source material
- Streaming responses for better user experience
- Developer evaluation mode for testing and improving responses

## Key Components
1. **Flask Web Application**: Serves the frontend and handles API requests
2. **RAG Assistant**: Core logic for retrieval and generation
3. **Search Integration**: Connects to Azure Search for knowledge retrieval
4. **OpenAI Integration**: Leverages Azure OpenAI for response generation
5. **Developer Tools**: Evaluation and testing capabilities

## Technical Requirements
- Python Flask backend
- Azure OpenAI API integration
- Azure Search integration
- Frontend with HTML/CSS/JavaScript
- Streaming response capabilities
- Parameter customization for model responses

## Goals
1. Provide accurate, contextually relevant responses to user queries
2. Properly cite sources of information
3. Allow customization of system prompts and model parameters
4. Support developer evaluation and testing
5. Maintain a responsive and user-friendly interface

## Success Criteria
- Accurate retrieval of relevant information from the knowledge base
- High-quality, contextually appropriate responses
- Proper citation of sources
- Smooth user experience with streaming responses
- Effective developer evaluation capabilities
