from locust import HttpUser, task, between

class LoadBalancerTest(HttpUser):
    wait_time = between(1, 3)  # ✅ Simulate real users with a wait time of 1-3 seconds

    @task
    def send_post_request(self):
        """ Simulates a client sending a POST request to the load balancer """
        payload = {
            "game": "Mobile Legends",
            "gamerID": "TEST_USER",
            "points": 50
        }
        headers = {"Content-Type": "application/json"}
        
        response = self.client.post("/api/process/", json=payload, headers=headers)
        if response.status_code != 200:
            print(f"❌{response}")
