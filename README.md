# URL Response Code Checker

A high-performance Python utility for validating and auditing large lists of URLs in parallel.  
Reads an input CSV with `URL`, `Langs`, and `Status` columns, checks each link’s HTTP response code (e.g., 200, 404, 500), and writes the results to a timestamped CSV.

---

## 🚀 Features

- ⚡ **Concurrent requests** via `ThreadPoolExecutor` — handles 1,000+ URLs efficiently  
- 🧾 **CSV input/output** with normalized headers  
- 🧠 **Header normalization** — handles Excel quirks, UTF-8 BOMs, and spacing/case differences  
- 🎨 **Color + emoji console output** for instant visual scanning  
- 🕓 **Timestamped results** for easy version tracking  
- 📁 **Flexible output directory** — defaults to the script’s folder or specify via `-o`  
- 🔁 **Smart fallback** from `HEAD` → `GET` if a server blocks HEAD requests  

---

## 🧰 Requirements

- Python 3.8+
- Install dependencies:
  ```bash
  pip install requests colorama

## ⚙️ Usage
- Basic command
`python check_urls_response_code.py -i urls.csv`

Specify an output directory
`python check_urls_response_code.py -i urls.csv -o ./results/`


The script will generate an output file such as:
`urls_results_20251023_231200.csv`

by default in the same folder as the script (or in the directory you specify).

## 🧩 Input Format
**Example urls.csv:**

```
URL,Langs,Status
https://www.google.com,en,Active
https://www.exabeam.com,en,Active
https://example.com/does-not-exist,en,Inactive
```

## 🧾 Output Format
**Example output:**

```
URL,Langs,ResponseCode,Status
https://www.google.com,en,200,Active
https://www.exabeam.com,en,200,Active
https://example.com/does-not-exist,en,404,Inactive
```

## 🎨 Color & Emoji Legend
Emoji	Meaning	Range / Type
- 🟩	Success	200–299
- 🟨	Redirect	300–399
- 🟥	Client or Server Error	400–599
- ⚫	Timeout / Connection Failure	“ERROR”

Example console output:

## 🔍 Checking 1,245 URLs using up to 50 threads...
- 🟩 https://www.google.com -> 200
- 🟩 https://www.exabeam.com -> 200
- 🟥 https://example.com/does-not-exist -> 404
- ⚫ https://timeout-domain.xyz -> ERROR

✅ Results written to: C:\Projects\URLChecker\urls_results_20251023_231200.csv

## ⚡ Performance Tuning
You can modify these constants at the top of the script for your system/network:

- MAX_WORKERS = 50  # Number of concurrent threads (50–100 is ideal)
- TIMEOUT = 10      # Seconds to wait per request

Increasing MAX_WORKERS speeds up large batches but uses more network bandwidth.
Lower TIMEOUT values will skip slow or unresponsive sites faster.

## 🧑‍💻 Development Setup
```git clone https://github.com/<yourusername>/url-response-checker.git```
`cd url-response-checker`

### Create and activate a virtual environment
`python -m venv venv`
`venv\Scripts\activate   # Windows`
 or
`source venv/bin/activate   # macOS/Linux`

### Install dependencies
```pip install requests colorama```

### Run the script
```python check_urls_response_code.py -i urls.csv```

## 💡 Example Use Cases
- Validate large website link sets for SEO or migration QA
- Audit multi-language content URLs (Langs column)
- Verify partner or vendor availability across global domains
- Track redirect and uptime behavior across URLs
- Test API endpoints for availability and latency issues
