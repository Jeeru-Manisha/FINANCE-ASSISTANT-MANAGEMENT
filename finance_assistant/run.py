from app.main import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting AI-Powered Personal Finance Assistant...")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)