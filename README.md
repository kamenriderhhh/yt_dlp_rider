# yt_dlp_rider
This project is intended for personal usage and hope one day able to contribute to the society and this is deeply inspired by below references:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [EasyExtractSenchou](https://github.com/ShimamuX/EasyExtractSenchou)

---

## Features
[WIP]
Download video via url: DONE
Upload video via script: WIP

## Usages
#### Install python 3.10 and pip install uv

Initialize project/environment
```
uv sync
```
Then run the python script with replace the url with actual YT video url
```
uv run main.py -l [url]
```

## uv
uv related commands
```
# Init uv project
uv init
# import requirements.txt to pyproject.toml
uv add -r requirements.txt
# To run script
uv run xxxx.py
# To lock dependencies declared in a pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
# To sync an environment with a xxx file:
uv pip sync requirements.txt
uv pip sync requirements.txt
```

