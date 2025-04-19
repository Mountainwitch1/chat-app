# Chat Application

This is a real-time chat application built using Flask, Flask-SocketIO, and Flask-Login. It allows users to sign up, log in, send messages, and create groups for chatting.

**Note:** This project is still in progress. Some features may not be fully implemented or may undergo changes.

## Features

- User authentication (Sign up, Log in, Log out)
- Real-time messaging using WebSockets
- Group creation with unique invite links
- Messages expire after 12 hours
- Notifications for new messages

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chat-app
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -c "from msg.app import db; db.create_all()"
   ```

5. Run the application:
   ```bash
   python msg/app.py
   ```

6. Access the application in your browser at `http://localhost:5001`.

## Usage

1. **Sign Up**: Create a new account.
2. **Log In**: Log in with your credentials.
3. **Chat**: Send and receive real-time messages.
4. **Create Groups**: Create a group and share the invite link with others.

## File Structure

```
chat-app/
├── msg/
│   ├── app.py          # Main application file
│   ├── templates/      # HTML templates
│   ├── static/         # Static files (CSS, JS)
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
```

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-SocketIO
- Flask-Login

Install all dependencies using:
```bash
pip install -r requirements.txt
```

## License

This project is open-source and available under the [MIT License](LICENSE).
