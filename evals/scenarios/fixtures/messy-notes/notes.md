# Tern notes

## Setup
Install Python 3.11, then run `pip install -r requirements.txt`. Copy `config.example.toml` to `config.toml` and set `slides_dir`. Run `tern sync` once to check that the login works.

## Meeting 2026-09-30
Present: Jonah, Mara. We agreed that the first release covers only PDF slides. Mara will check the university login flow. Release rule: releases go out on Fridays so that the weekend can absorb problems.

## Architecture ideas
The sync loop reads a course list, asks the portal for new files and downloads them. An event bus between the loop and the downloader would allow a progress bar later. Retries use exponential backoff, starting at 2 seconds. The download cache is keyed by file hash.

## TODO
- add the progress bar
- write tests for the retry logic
- handle expired sessions
- decide on a name for the config file section

## Meeting 2026-10-07
Present: Jonah, Mara, Lukas. Mara found that the login flow needs a second factor. Lukas suggested supporting video files in a later release. New release rule: no releases on Fridays anymore, because nobody is around to fix problems on weekends. Next meeting is on 2026-10-21.

## Troubleshooting
If `tern sync` reports "session expired", delete `~/.tern/session.json` and log in again. If downloads stall, lower `parallel_downloads` in `config.toml` to 2.
