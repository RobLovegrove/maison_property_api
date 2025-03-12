from app import create_app
import time

def run_test():
    print("Creating test app...")
    app = create_app("testing")
    client = app.test_client()
    
    print("Starting test...")
    start_time = time.time()
    
    user_data = {
        "user_id": "test-user-123",  # Firebase UID
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "roles": [{"role_type": "buyer"}]
    }
    
    print("Sending POST request...")
    response = client.post("/api/users", json=user_data)
    
    print(f"Response received in {time.time() - start_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.get_json()}")
    
    if response.status_code == 201:
        print("Test passed!")
    else:
        print("Test failed!")

if __name__ == "__main__":
    run_test() 