# Chat With Codebase - Frontend

This is the Flutter frontend for the "Chat With Codebase" application. It provides a clean, cross-platform chat interface to interact with your codebase using a Retrieval-Augmented Generation (RAG) backend.

## Features
- **Cross-Platform**: Runs on web, iOS, Android, and desktop natively.
- **Repository Ingestion**: Trigger repository parsing directly from the UI.
- **Interactive Chat**: Send queries and receive context-aware responses with source citations.
- **Modern UI**: Clean and intuitive chat interface built with Flutter widgets.

## Getting Started

### Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (Ensure you have the latest stable version)
- The backend API must be running locally (default: `http://localhost:8000`)

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run the application:
   ```bash
   flutter run
   ```
   *Note: For Chrome/Web, use `flutter run -d chrome`*

## Environment Setup
By default, the app expects the backend to be running on localhost. If you deploy the backend, you'll need to update the API base URL in the Dart services.

## Built With
* [Flutter](https://flutter.dev/) - UI Toolkit
* [Dart](https://dart.dev/) - Language
