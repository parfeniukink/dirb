# Dirb (In progress)

This is an extended version of a [dirb](https://www.kali.org/tools/dirb/) spider.

Beautifulsoup used here to search the specific content on the page.


## Installation

### Requirements
- [Python3.7+](https://www.python.org/downloads/)

### Setup environment
```bash
# Create Python isolated environment and activate it
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

<br>

## Usage

### Run the script
```bash
(venv) python run.py <base_url>
```
> Note: Currently, Base URL need a SLASH in the end


### Customization
Currently, all changes can be done by modifying `run.py`

- `CHUNK_SIZE` -- The amount of urls in a single async batch. Less is better
- `TEXT_TO_MATCH` -- The list of words or phrases you do not expect to see in success response
- `WORDLIST_FILENAME` -- The name of the wordlist `.txt` file.
- `RESULTS_FILENAME` -- The name of the results file. Note: you also have the output with results in your Terminal
