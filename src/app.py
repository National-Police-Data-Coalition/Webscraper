import json
import logging
from scraping.FiftyA import FiftyA
from scraping.ScrapeCache import ScrapeCacheContainer
from scraping.Producer import ProducerContainer


def main(logger: logging.Logger) -> None:
    # Read the data from FiftyA
    fiftya = FiftyA(logger) 
    officers = fiftya.extract_data()

    # Connect to the cache and a producer
    cache_container = ScrapeCacheContainer("REDIS")
    producer_container = ProducerContainer("REDIS")
    redis_cache = cache_container.get_cache()
    redis_pub = producer_container.get_queue()


    for officer in officers:
        if not officer:
            continue
        officer.pop("complaints")

        tax_id = str(officer.get("taxId", ""))
        if not tax_id:
            logger.warning(f"Could not find tax id for officer {officer['first_name']} {officer['last_name']}")
            continue
        logger.info(f"Processing officer {tax_id}")
        # Check if officer is already in cache
        if redis_cache.get_json(tax_id):
            cached_officer = redis_cache.get_json(tax_id)
            if cached_officer == officer:
                continue
        logger.info(f"Found new officer {tax_id}")
        # If officer is not in cache, add them to cache and publish to queue
        officer["work_history"] = "\r\n".join(officer["work_history"])
        logger.info(f"Adding officer {tax_id} to cache")
        redis_cache.set_json(tax_id, officer)
        logger.info(f"Published officer {tax_id}")
        redis_pub.publish("officers", json.dumps(officer))



        
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    main(logger)
    # schedule.every(1).days.do(main)

    # while True:
    #     print("Running main")
    #     schedule.run_pending()
    #     time.sleep(1)
