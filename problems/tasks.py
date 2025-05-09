# # # import threading
# # # import requests
# # # from .models import ProblemCompletion
# # # from .utils import analyze_code_with_ai
# # #
# # #
# # # def fetch_ai_analysis_async(problem_completion):
# # #     from django.utils import timezone
# # #
# # #     def task():
# # #         code_url = problem_completion.solution_url
# # #         problem = problem_completion.problem
# # #         try:
# # #             print(f"Attempting to fetch code from: {code_url}")
# # #             code_response = requests.get(code_url)
# # #             code_response.raise_for_status()  # Check if the request was successful
# # #             code = code_response.text
# # #             print(f"Code fetched successfully for {code_url}")
# # #
# # #             # Now try analyzing the code
# # #             ai_result = analyze_code_with_ai(code, problem.description)
# # #             if ai_result:
# # #                 # Update the ProblemCompletion model with the AI analysis
# # #                 problem_completion.ai_analysis = ai_result
# # #                 problem_completion.save()
# # #                 print(f"AI analysis successful for {code_url}")
# # #             else:
# # #                 print(f"AI analysis returned no result for {code_url}")
# # #
# # #         except requests.exceptions.RequestException as e:
# # #             print(f"Error fetching code from {code_url}: {e}")
# # #         except Exception as e:
# # #             print(f"AI analysis failed for {code_url}: {e}")
# # #
# # #     threading.Thread(target=task).start()
# #
# # import threading
# # import time
# # import requests
# # from .models import ProblemCompletion
# # from .utils import analyze_code_with_ai
# # from django.utils import timezone
# #
# # # Global variables for rate limiting
# # request_count = 0
# # last_reset_time = time.time()
# # rate_limit_lock = threading.Lock()
# #
# # # Function to check and update the rate limit counter
# # def check_rate_limit():
# #     global request_count, last_reset_time
# #
# #     # Lock to ensure thread safety
# #     with rate_limit_lock:
# #         # Check if it's time to reset the count (i.e., after 1 minute)
# #         if time.time() - last_reset_time >= 60:
# #             request_count = 0
# #             last_reset_time = time.time()
# #
# #         # Check if the number of requests exceeds the limit
# #         if request_count < 15:
# #             request_count += 1
# #             return True
# #         else:
# #             return False
# #
# #
# # def fetch_ai_analysis_async(problem_completion):
# #     def task():
# #         if not check_rate_limit():
# #             print("Rate limit exceeded. Try again later.")
# #             return
# #
# #         code_url = problem_completion.solution_url
# #         problem = problem_completion.problem
# #
# #         try:
# #             print(f"Attempting to fetch code from: {code_url}")
# #             code_response = requests.get(code_url)
# #             code_response.raise_for_status()  # Check if the request was successful
# #             code = code_response.text
# #             print(f"Code fetched successfully for {code_url}")
# #
# #             # Now try analyzing the code
# #             ai_result = analyze_code_with_ai(code, problem.description)
# #             if ai_result:
# #                 # Update the ProblemCompletion model with the AI analysis
# #                 problem_completion.ai_analysis = ai_result
# #                 problem_completion.save()
# #                 print(f"AI analysis successful for {code_url}")
# #             else:
# #                 print(f"AI analysis returned no result for {code_url}")
# #
# #         except requests.exceptions.RequestException as e:
# #             print(f"Error fetching code from {code_url}: {e}")
# #         except Exception as e:
# #             print(f"AI analysis failed for {code_url}: {e}")
# #
# #     threading.Thread(target=task).start()
#
# import threading
# import time
# import requests
# from .models import ProblemCompletion
# from .utils import analyze_code_with_ai
# from django.utils import timezone
#
# # Global variables for rate limiting
# request_count = 0
# last_reset_time = time.time()
# rate_limit_lock = threading.Lock()
#
# # Function to check and update the rate limit counter
# def check_rate_limit():
#     global request_count, last_reset_time
#
#     # Lock to ensure thread safety
#     with rate_limit_lock:
#         # Check if it's time to reset the count (i.e., after 1 minute)
#         if time.time() - last_reset_time >= 60:
#             request_count = 0
#             last_reset_time = time.time()
#
#         # Check if the number of requests exceeds the limit
#         if request_count < 15:
#             request_count += 1
#             return True
#         else:
#             return False
#
#
# def fetch_ai_analysis_async(problem_completion):
#     def task():
#         # Check if rate limit is exceeded
#         if not check_rate_limit():
#             print("Rate limit exceeded. Try again later.")
#             return
#
#         code_url = problem_completion.solution_url
#         problem = problem_completion.problem
#
#         try:
#             print(f"Attempting to fetch code from: {code_url}")
#             code_response = requests.get(code_url)
#             code_response.raise_for_status()  # Check if the request was successful
#             code = code_response.text
#             print(f"Code fetched successfully for {code_url}")
#
#             # Now try analyzing the code
#             ai_result = analyze_code_with_ai(code, problem.description)
#             if ai_result:
#                 # Update the ProblemCompletion model with the AI analysis
#                 problem_completion.ai_analysis = ai_result
#                 problem_completion.save()
#                 print(f"AI analysis successful for {code_url}")
#             else:
#                 print(f"AI analysis returned no result for {code_url}")
#
#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching code from {code_url}: {e}")
#         except Exception as e:
#             print(f"AI analysis failed for {code_url}: {e}")
#
#     threading.Thread(target=task).start()

import threading
import time
import queue
import requests
from .models import ProblemCompletion
from .utils import analyze_code_with_ai

# Queue for task scheduling
task_queue = queue.Queue()

# Lock-protected shared rate limit variables
request_count = 0
last_reset_time = time.time()
rate_limit_lock = threading.Lock()

# Worker function that runs in a single thread
def worker():
    global request_count, last_reset_time
    while True:
        problem_completion = task_queue.get()
        if problem_completion is None:
            break  # Exit signal

        with rate_limit_lock:
            # Reset counter if 60 seconds have passed
            if time.time() - last_reset_time >= 60:
                request_count = 0
                last_reset_time = time.time()

            if request_count >= 15:
                print("Rate limit hit — sleeping for 60 seconds...")
                time.sleep(60)
                request_count = 0
                last_reset_time = time.time()

            request_count += 1

        process_problem_completion(problem_completion)
        task_queue.task_done()


def process_problem_completion(problem_completion):
    code_url = problem_completion.solution_url
    problem = problem_completion.problem

    try:
        print(f"Fetching code from: {code_url}")
        code_response = requests.get(code_url)
        code_response.raise_for_status()
        code = code_response.text.strip()

        if not code:
            print(f"No code at {code_url}. Skipping.")
            return

        ai_result = analyze_code_with_ai(code, problem.description)
        if ai_result and not ai_result.lower().startswith(("no code submitted", "ai request failed", "gemini api error")):
            problem_completion.ai_analysis = ai_result
            problem_completion.save()
            print(f"Saved AI analysis for {code_url}")
        else:
            print(f"AI analysis invalid or failed for {code_url}")

    except requests.exceptions.RequestException as e:
        print(f"HTTP error for {code_url}: {e}")
    except Exception as e:
        print(f"Error processing {code_url}: {e}")


# Start the background worker thread
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()


# This function queues the task instead of running it immediately
def fetch_ai_analysis_async(problem_completion):
    task_queue.put(problem_completion)
