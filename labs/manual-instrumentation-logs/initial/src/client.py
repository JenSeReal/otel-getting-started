import time
import os
import random
from abc import ABC, abstractmethod
from faker import Faker
from model.user import User

class UserInterface(ABC):
   @abstractmethod
   def get_user(self, id: int) -> tuple[User, int]:
       pass

# simulates a database
class FakerClient(UserInterface):
    def __init__(self):
        self.faker = Faker()

    def get_user(self, id: int) -> tuple[User, int]:
        usr = User(
            id = random.randint(1, 1000),
            name = self.faker.name(),
            address = self.faker.address()
        )
        return usr

# wraps another client for Application-level fault injection
class ChaosClient(UserInterface):
    def __init__(self, client: UserInterface, base_delay: int = 50):
        self.client = client
        self.base_delay = base_delay
        self.request_type = ["fast", "medium", "slow"]
        self.request_probability = (.80, .15, .05)
        self.request_latency = {
            "fast": 100,
            "medium": 300,
            "slow": 2000,
        }
        self.response_status = ["success", "fail"]
        self.response_code_probability = (.90, .10)

    def get_user(self, id: int) -> tuple[User, int]:
        faults_enabled = (os.getenv("CHAOS", "false").lower() == "true")
        if faults_enabled: 
            # add latency
            additional_latency = self.request_latency[random.choices(self.request_type, self.request_probability)[0]]
            time.sleep(self.base_delay/1000)
            time.sleep(additional_latency/1000)

            # choose status code
            status = random.choices(self.response_status, self.response_code_probability)[0]
            if status == "success":
                return self.client.get_user(id), 200
            elif status == "fail":
                return None, 404

        return self.client.get_user(id), 200