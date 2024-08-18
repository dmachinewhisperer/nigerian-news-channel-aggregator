# Scraper

**Scraper** is a tool that pulls RSS feed data from various news publishers and aggregates the news items into a table where each entry is not more than a specified time old.

## Database

The tool is backed by SQLite database with tables:

### a. Historical

Stores all news items retrieved permanently.

| Column       | Type    | Description                          |
|--------------|---------|--------------------------------------|
| `id`         | INTEGER | Primary key, nth entry               |
| `name`       | TEXT    | Name of the publisher as in `sites.json` |
| `pubDate`    | TEXT    | Date and time of item publication    |
| `title`      | TEXT    | Title of the news item               |
| `description`| TEXT    | News item summary                    |
| `link`       | TEXT    | Link to the news item                |

### b. Current

Fresh articles are kept here. The tool automatically removes old articles outside a time window and adds new ones.

- **Schema**: Same as the `Historical` table.

### c. last_processed

Tracks the last processed time of articles. When the scraper runs, if the `lastBuildDate` of the RSS feed is not newer than the last processed time entry in this table, the RSS file is skipped.

| Column            | Type    | Description                                      |
|-------------------|---------|--------------------------------------------------|
| `id`              | INTEGER | ID as in `sites.json`                            |
| `last_processed`  | TEXT    | Time the tool last touched the article           |

## Dependencies

- `pytz`
- `requests`

## Setting Up

### a. Configuration

The first lines of `scraper.py` configure the tool:

- `SQLITE_DATABASE_PATH = '../instance/app.db'`: Supply the path to the database (or where the database will be created if running for the first time).
- `SITE_RSS_FEED_URLS_PATH = './'`: Supply the path to the `sites.json`. See the Files section.
- `RSS_FOLDER = 'rss-feeds'`: Supply a staging area for processing the RSS feeds.
- `TIME_WINDOW_HOURS = 6`: Specify how many hours from the time of retrieval a news article is valid. The tool automatically cleans up articles in the `Current` table that are more than `TIME_WINDOW_HOURS` old, counting from the item publish date.

### b. Installation

Run `install.sh` to set up a systemd timer and unit files to automatically run the tool hourly (run period is adjustable in `install.sh`).

## Files

- `install.sh`: Shell script for installation.
- `dbtool.py`: Simple script for interacting with SQLite databases (it is self-documenting).
- `sites.json`: RSS links of Nigerian news publishers. Maintained here [https://github.com/dmachinewhisperer/nigerian-news-channel-rss-feeds](https://github.com/dmachinewhisperer/nigerian-news-channel-rss-feeds). A static copy is included here, but check the repo for the newest copies.

## License
MIT