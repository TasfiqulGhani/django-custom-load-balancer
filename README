# **Round Robin Load Balancer API**

## 📌 **Goal**
The objective of this project is to implement a **Round Robin Load Balancer** that distributes requests to multiple **Application API instances** in a **scalable and fault-tolerant** way.

**Key Features:**
- Implements **Round Robin Algorithm** to evenly distribute requests.
- Detects **unhealthy or slow instances** and routes traffic accordingly.
- Provides Test Cases.

---

## 🛠 **Planning & System Design**

### **Overall Workflow**

#### Core Flow

```mermaid
graph TD;
    %% Load Balancer and Server Flow %%
    User -->|Request| LoadBalancer[Load Balancer];

    LoadBalancer -->|Distribute Request| Server1[Server 1];
    LoadBalancer -->|Distribute Request| Server2[Server 2];
    LoadBalancer -->|Distribute Request| Server3[Server 3];

    %% Server Responses %%
    Server1 -->|Response| LoadBalancer;
    Server2 -->|Response| LoadBalancer;
    Server3 -->|Response| LoadBalancer;
    
    LoadBalancer -->|Send Response| User;

```

#
#### Health Checker Flow

```mermaid
graph TD;
    %% Health Checker Flow %%
    Start[Health Checker Starts] -->|Fetch Active Containers| FetchInstances;
    
    FetchInstances -->|Check if Running| ActiveContainers{Are Containers Running?};

    %% If Containers are Running %%
    ActiveContainers -- Yes --> CheckHealth[Perform Health Check];

    %% Health Checks %%
    CheckHealth -->|Check CPU Usage| CheckCPU{CPU < Threshold?};
    CheckCPU -- No --> MarkFailed[Move to Failed List & Stop Using];

    CheckHealth -->|Check Memory Usage| CheckMemory{Memory < Threshold?};
    CheckMemory -- No --> MarkFailed;

    CheckHealth -->|Ping Health URL| CheckHealthURL{Response OK?};
    CheckHealthURL -- No --> MarkFailed;

    %% If All Checks Pass %%
    CheckCPU -- Yes --> PassedCPU;
    CheckMemory -- Yes --> PassedMemory;
    CheckHealthURL -- Yes --> PassedURL;
    
    PassedCPU --> PassedMemory;
    PassedMemory --> PassedURL;
    PassedURL --> AddToHealthy[Add to Healthy List];

    %% If Containers are Not Running %%
    ActiveContainers -- No --> RemoveFailed[Remove from Healthy List];

    %% Periodic Health Checks %%
    PeriodicCheck[Runs Every X Seconds] -->|Verify Health| CheckHealth;
    
    %% Error Handling %%
    MarkFailed -->|Retry if Possible| RetryInstance[Retry with Another Healthy Instance];
    RetryInstance -- No Healthy Left --> Error[No Available Instances];

```

---

## 🎯 **Design Patterns Used**
We applied the **Gang of Four (GoF)** design patterns to create a structured and maintainable system.

### **1️⃣ Creational Patterns**
- **Singleton Pattern** `HealthChecker` 
  - Ensures that only one health checker is responsible for monitoring all instances.

### **2️⃣ Structural Patterns**
- **Proxy Pattern** → `RoundRobinProxy`  
  - Acts as a proxy between users and backend application instances.

### **3️⃣ Behavioral Patterns**
- **Strategy Pattern** → `LoadBalancer`  
  - The Load Balancer uses different request distribution strategies.

## 📂 **Project Structure & File Descriptions**
| File / Directory | Description |
|-----------------|-------------|
| `round_robin/` | Contains core load balancing logic |
| `round_robin/proxy.py` | Implements the Round Robin algorithm |
| `round_robin/factory.py` | **Factory Pattern** for dynamic proxy creation |
| `monitoring/health_checker.py` | **Health Monitoring & Circuit Breaker** |
| `monitoring/system_monitor_docker.py` | Monitors **CPU & Memory** usage via Docker API |
| `adapters/docker_adapter.py` | **Adapter Pattern** for Docker communication |
| `instance_manager.py` | **Auto-detects running API instances** dynamically |
| `tests/` | Contains **unit & integration tests** |
| `locustfile.py` | **Performance testing** using Locust |
| `docker-compose.yml` | Defines **Docker containers** for easy scaling |

---

## 🛡 **Advanced Circuit Breaker in Health Checker**
We implement an **intelligent circuit breaker** in `health_checker.py` to handle **API failures** dynamically.

### 🚨 **Circuit Breaker Features**
✅ **Detects failures** (timeouts, errors, and crashes).  
✅ **Prevents overloading** failing instances.  
✅ **Automatically recovers** once an instance becomes healthy.  

📄 **health_checker.py**
```python
import time
import threading
import requests
from django.conf import settings
from ..monitoring.system_monitor_docker import DockerSystemMonitor
from ..adapters.docker_adapter import DockerAdapter

class HealthChecker:
    """ ✅ Monitors instances via Docker and prevents overloading failing servers """

    def __init__(self, instance_manager, system_monitor: DockerSystemMonitor):
        self.instance_manager = instance_manager
        self.system_monitor = system_monitor
        self.docker_adapter = DockerAdapter()
        self.failed_instances = set()  # ✅ Tracks failing instances
        self.running = True

        # ✅ Start background health check process
        self.health_check_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        self.health_check_thread.start()

    def health_check_loop(self):
        """ ✅ Runs every 5 seconds to check instance health and refresh instances """
        while self.running:
            time.sleep(settings.HEALTH_CHECK_INTERVAL)
            self.instance_manager.refresh_instances()  # ✅ Fetch latest running instances
            self.check_instances_health()

    def check_instances_health(self):
        """ ✅ Checks if instances are running and removes them from the failed list if healthy """
        for instance_url in list(self.failed_instances):
            container_name = instance_url.replace("http://", "").split(":")[0]

            is_running = self.docker_adapter.get_container_status(container_name) == "running"
            is_healthy = self.is_application_healthy(instance_url)

            if not is_running:
                self.failed_instances.add(instance_url)
                continue  

            is_overloaded = self.is_container_overloaded(container_name)

            if is_running and not is_overloaded and is_healthy:
                self.failed_instances.remove(instance_url)

    def is_application_healthy(self, instance_url):
        """ ✅ Checks if the application is responding to health check API """
        health_url = instance_url.replace("/api/process/", "/api/process/health")

        try:
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False  

    def is_container_overloaded(self, container_name):
        """ ✅ Uses DockerSystemMonitor to check CPU & Memory usage """
        cpu_usage = self.system_monitor.get_cpu_usage(container_name)
        memory_usage = self.system_monitor.get_memory_usage(container_name)

        return cpu_usage > settings.CPU_THRESHOLD or memory_usage > settings.MEMORY_THRESHOLD

    def mark_failed(self, instance_url):
        """ ✅ Adds instance to the failed list (Used when request fails) """
        self.failed_instances.add(instance_url)

    def stop(self):
        """ ✅ Gracefully stop the health checker """
        self.running = False
```
### 🛡️ **Security & Attack Protection**
✅ **Attack Detection & Mitigation:** If an IP exceeds a suspicious request threshold, stricter throttling is applied.

✅ **Environment-Based Throttling** Default rate limits are set via environment variables.

---

## ✅ **How It Fulfills Requirements**
### **Handling API Failures**
- If an **application API goes down**, the load balancer **removes it** from the available instances.
- The **HealthChecker** continuously monitors APIs and **re-adds them** if they recover.

### **Handling Slow APIs**
- If an instance starts responding **slowly**, the **HealthChecker** detects latency, CPU usage and Memory usage and if its bellow threshold we dont use that instance till its in good condition.

### **Testing Strategy**
We use **Django's unittest framework** and **Locust** for performance benchmarking.
- **Unit Tests:** Validate individual components.
- **Integration Tests:** Ensure smooth end-to-end communication.
- **Performance Tests:** Check system efficiency under high loads.(Using locust)

---

---

## 🚀 **How to Run the Project**
### **Step 1: Go to root**
```bash
cd django_round_robin/
```

### **Step 2: Build & Start Services**
```bash
docker-compose up --build
```
> This will start **3 application instances** and the **round robin proxy**.
  
### **Step 4: Run Performance Tests**
> Docker compose also handling the locust initialzation. Its completly automatic.

Then visit **http://localhost:8089** to configure & run tests.

---

## 📡 **API Endpoints**
### **Process Request (Forwarded via Load Balancer)**
```bash
curl --location 'http://localhost:8080/api/process/' \
--header 'Content-Type: application/json' \
--data '{
    "game": "Mobile Legends",
    "gamerID": "GYUTDTE",
    "points": 20
}'
```
✅ **Expected Response:**
```json
{
    "game": "Mobile Legends",
    "gamerID": "GYUTDTE",
    "points": 20
}
```

---

