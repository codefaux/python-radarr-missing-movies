# python-radarr-missing-movies

## -- A NOTE FROM THE 'AUTHOR' --

As a test, I've been writing this via ChatGPT. __I am not an AI advocate.__ AI can be dangerous, and putting it "in charge" is a mistake. I know Python well enough to work on this code, but getting off the ground is always a challenge, so I wanted to literally just talk ChatGPT through it, to see how the experience went. I discourage using ChatGPT (or any other AI model) when you are not also personally familiar with the material you're asking for. If you don't know what garbage looks like, you can't judge if AI has given you garbage. I'm very encouraged by the results, as I've not modified any of its output by hand, except this note.

You're welcome to use this code, and submit issues, and I'll also consider feature requests, but I will not accept pull requests as my intent is to make ChatGPT fully responsible for modifications to code.

Here is [a link](https://chatgpt.com/share/67673225-e1ec-8004-8816-3bf31728ff7f) to the actual conversation used to create this code, in case anyone cares to look. I've been informal and sometimes indirect with the AI, intentionally attempting to test the bounds of its comprehension. I may forget to update this link if I make changes, feel free to request an update as an issue.

I am actually using this on my live system, and I have to say, I'm quite pleased with the results.

Now, on with the show..

# Overview
This repository provides a Python script to automate searching for missing movies in Radarr. The script interacts with Radarr and SABnzbd APIs to ensure efficient and timely searches. The script avoids redundant searches and respects rate limits to prevent overloading your services.

## Features
- Fetches a list of missing movies from Radarr.
- Avoids searching for the same movie twice by maintaining an archive of searched movies (`archive.lst`).
- Ensures a movie is released before performing a search.
- Integrates with SABnzbd to prevent new searches when the queue is too busy.
- Dynamically calculates sleep intervals based on the remaining time of the first unpaused queue item in SABnzbd.
- Configurable via command-line arguments.

## Requirements
- Python 3.6 or higher.
- Installed and running instances of Radarr and SABnzbd.
- API keys for Radarr and SABnzbd.

## Installation
Clone the repository:
```bash
git clone https://github.com/codefaux/python-radarr-missing-movies.git
cd python-radarr-missing-movies
```

## Usage
Run the script with the following command:
```bash
./radarr_missing_movies.py --radurl <RADARR_URL> --radapikey <RADARR_API_KEY> --saburl <SABNZBD_URL> --sabapikey <SABNZBD_API_KEY>
```

### Example
```bash
./radarr_missing_movies.py --radurl http://localhost:7878 --radapikey your_radarr_api_key --saburl http://localhost:8080 --sabapikey your_sabnzbd_api_key --queue-limit 3 --sab-sleep 120 --radarr-sleep 180
```

### Detaching Sessions
To run the script persistently without keeping the terminal open, use a session manager like `tmux`:
1. Start a `tmux` session:
   ```bash
   tmux new -s radarr_script
   ```
2. Run the script inside the `tmux` session.
3. Detach the session by pressing `Ctrl-b` followed by `d`.
4. Reattach later with:
   ```bash
   tmux attach -t radarr_script
   ```

## Configuration
The script supports the following command-line arguments:
- `--radurl`: Base URL of the Radarr instance (required).
- `--radapikey`: API key for Radarr (required).
- `--saburl`: Base URL of the SABnzbd instance (required).
- `--sabapikey`: API key for SABnzbd (required).
- `--queue-limit`: Maximum number of items allowed in the SABnzbd queue before triggering a new search (default: `5`).
- `--sab-sleep`: Minimum sleep interval (in seconds) between SABnzbd queue checks (default: `60`).
- `--radarr-sleep`: Sleep interval (in seconds) between Radarr searches (default: `60`).
- `--no-movies-sleep`: Sleep interval (in seconds) when no missing movies are found (default: `3600`).

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contribution
Contributions, issues, and feature requests are welcome! Feel free to open an issue or create a pull request.

