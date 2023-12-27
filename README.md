# Concept Web Scraper

This project is a Python-based web scraping application designed to extract, cache, and publish data from a target website. The application is built to run periodically, ensuring the most recent data is always available.

## Architecture

The main script, `app.py`, orchestrates the process by leveraging classes from the `scraping` module. The `FiftyA` class is responsible for the actual web scraping, while `ScrapeCacheContainer` and `ProducerContainer` manage caching and data publishing, respectively.

The `Scraper` class in `scraping/Scraper.py` is a generic web scraper, equipped with a list of user-agent headers to rotate through for requests, a common technique to avoid being blocked by the target website.

## Deployment

The project is containerized using Docker, allowing for easy deployment and scaling. The application and a Redis server are run as separate services, as defined in the `docker-compose.yml` file.

## Future Improvements

1. **Error Handling**: Enhance error handling, especially for network errors during web scraping.
2. **Logging**: Improve logging to provide more insight into the application's operation and performance.
3. **Testing**: Add unit tests to ensure the reliability of the code.
4. **Data Validation**: Validate data before caching and publishing to ensure its integrity.
5. **Scalability**: Consider ways to scale the scraping process, such as distributed scraping, if the amount of data to be scraped is large or grows over time. Ideally with seperate workers, we can improve performance and avoid getting blocked from servers.

