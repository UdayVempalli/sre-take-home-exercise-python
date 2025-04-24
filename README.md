# Installation and running instructions


## Clone the Repository

1. Open a terminal or command prompt
2. Clone the repository using the following command:

```bash
git clone https://github.com/UdayVempalli/sre-take-home-exercise-python.git
cd sre-take-home-exercise-python
```

## Install Requirements

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

If you prefer to install the dependencies manually:

```bash
pip install pyyaml requests
```

## Running the Application

Once you have cloned the repository and installed the requirements, you can run the application using:

```bash
python main.py sample.yaml
```

# Initial Code Review

## Application Overview

The application is a health monitoring tool for web service endpoints. It performs the following functions:

1. Loads endpoint configurations from a YAML file
2. Periodically checks if these endpoints are available
3. Calculates and displays availability percentages by domain
4. Runs these checks in cycles with 15-second intervals

After running the code it failed with following errors

![alt text](<screenshots/Screenshot 2025-04-22 120642.png>)

## Error Analysis

The main issue causing the error in the screenshot is in the `check_health` function of the original code. When an endpoint doesn't specify a method in the YAML file, the following line:

```python
method = endpoint.get('method')
```

Returns `None`. Later, when the requests library processes this value and tries to call:

```python
method.upper()
```

It fails because `None` doesn't have an `upper()` method, resulting in the error:

```
AttributeError: 'NoneType' object has no attribute 'upper'
```

## Missing requirements and Changes

After analyzing the original code against the requirements, I identified several issues that needed to be addressed. Here's what I found and fixed:

### 1. Default HTTP Method
The original code didn't provide a default value when the method field was missing in the YAML configuration. This caused the error we saw where `None` was being passed to the requests library, which then failed when trying to call `.upper()` on it. I fixed this by adding 'GET' as the default method:

```python
# Original code
method = endpoint.get('method')

# Updated code
method = endpoint.get('method', 'GET').upper()
```

This change ensures that when a method isn't specified, the code defaults to using GET as required.

### 2. Response Time Check
The original health check was only verifying the status code, but the requirements specify that endpoints must also respond within 500ms. I added timing code to measure how long each request takes and only mark them as "UP" if they're both returning a good status code AND responding quickly enough:

```python
# Original code
if 200 <= response.status_code < 300:
    return "UP"

# Updated code
start_time = time.time()
response = requests.request(method, url, headers=headers, json=body, timeout=5)
elapsed_ms = (time.time() - start_time) * 1000  # in milliseconds

if 200 <= response.status_code < 300 and elapsed_ms <= 500:
    return "UP"
```

This ensures we're properly checking both criteria for availability.

### 3. Request Timeout
The original code didn't set any timeout for requests, which could cause the application to hang indefinitely if an endpoint wasn't responding. I added a timeout parameter to prevent this:

```python
# Original code had no timeout
response = requests.request(method, url, headers=headers, json=body)

# Updated code
response = requests.request(method, url, headers=headers, json=body, timeout=5)
```

Adding this timeout prevents the application from getting stuck waiting for non-responsive endpoints.

### 4. Domain Extraction
The requirements specify that port numbers should be ignored when determining domains, but the original code wasn't handling this. I updated the domain extraction to properly remove port numbers:

```python
# Original code
domain = endpoint["url"].split("//")[-1].split("/")[0]

# Updated code
domain = url.split("//")[-1].split("/")[0].split(":")[0]  # Remove port if present
```

This change ensures that URLs like "example.com:8080" and "example.com" are correctly identified as the same domain.

### 5. Availability Calculation
The requirements explicitly state that decimal points should be dropped from availability percentages, but the original code was rounding them. I changed the calculation to use integer truncation instead:

```python
# Original code
availability = round(100 * stats["up"] / stats["total"])

# Updated code
availability = int(100 * stats["up"] / stats["total"])
```

This ensures the percentages are displayed as required, without rounding.

### 6. Consistent 15-Second Cycles
The original code always slept for exactly 15 seconds after completing all checks, but this didn't account for how long the checks themselves took. This resulted in cycles that were actually longer than 15 seconds. I fixed this by calculating the actual elapsed time and adjusting the sleep duration:

```python
# Original code
time.sleep(15)

# Updated code
elapsed = time.time() - cycle_start
time.sleep(max(0, 15 - elapsed))
```

This ensures each cycle starts exactly 15 seconds after the previous one began, regardless of how long the checks take.

### 7. Improved Output
While not explicitly required, I enhanced the output format to make the results clearer and more informative:

```python
# Original code
print(f"{domain} has {availability}% availability percentage")

# Updated code
print(f"--- Starting Check Cycle ---")
print(f"[{name}] ({domain}) status: {result}")
print(f"{domain}: {availability}% availability")
```

## Stopping the Application

To stop the monitoring application, press `Ctrl+C` in your terminal or command prompt.


## Result

![alt text](<screenshots/Screenshot 2025-04-23 220325.png>)

