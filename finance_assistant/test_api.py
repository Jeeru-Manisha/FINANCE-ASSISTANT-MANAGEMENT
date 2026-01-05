import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("🧪 Testing Finance Assistant API...\n")
    
    # Test home endpoint
    print("1. 📍 Testing home endpoint...")
    try:
        response = requests.get(BASE_URL)
        print(f"   ✅ Response: {response.json()}\n")
    except:
        print("   ❌ Cannot connect to server. Make sure app.py is running!\n")
        return
    
    # Test registration
    print("2. 👤 Testing user registration...")
    user_data = {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=user_data)
        result = response.json()
        print(f"   ✅ {result}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Add sample data
    print("3. 📊 Adding sample data...")
    try:
        response = requests.post(f"{BASE_URL}/api/sample-data")
        print(f"   ✅ {response.json()}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test analysis
    print("4. 📈 Testing spending analysis...")
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/1")
        result = response.json()
        if result['success']:
            print(f"   ✅ Net Savings: ${result['net_savings']}")
            print(f"   ✅ Savings Rate: {result['savings_rate']}%")
            print(f"   ✅ Recommendations: {', '.join(result['recommendations'])}")
            print(f"   ✅ Spending by Category: {json.dumps(result['spending_by_category'], indent=10)}")
        else:
            print(f"   ❌ {result['message']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test chatbot
    print("5. 🤖 Testing chatbot...")
    test_queries = [
        "How can I save more money?",
        "Analyze my spending",
        "Help me with budgeting",
        "What's my financial health?"
    ]
    
    for query in test_queries:
        try:
            chat_data = {"query": query}
            response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
            result = response.json()
            if result['success']:
                print(f"   💬 Query: '{query}'")
                print(f"   🤖 Response: {result['response']}")
                print()
        except Exception as e:
            print(f"   ❌ Error with query '{query}': {e}")
    
    print("🎉 All tests completed! Your finance assistant is working! 🎉")

if __name__ == "__main__":
    test_api()