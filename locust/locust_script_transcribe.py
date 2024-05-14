from locust import HttpUser, run_single_user, task
import logging


class QuickstartUser(HttpUser):
    #host = "http://ec2-35-172-178-196.compute-1.amazonaws.com:8080"
    @task
    def inference(self):
        fileIn = {
            "file": open('samples_jfk.wav', "rb"),
            "temperature": '0.0',
            "temperature_inc": '0.2',
            "response_format": 'json'
        }
        with self.client.post("/inference", files=fileIn) as response:
            logging.info("response: %s | status_code:%s",str(response.text),str(response.status_code))

# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(QuickstartUser)