import json
import schedule
import time
from scraping.FiftyA import FiftyA
from scraping.ScrapeCache import ScrapeCacheContainer
from scraping.Producer import ProducerContainer


def main():

    # Read the data from FiftyA
    fiftya = FiftyA() 
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

        badge = officer.get("badge", "")
        if not badge:
            continue
        print(f"Processing {badge}")
        # Check if officer is already in cache
        if redis_cache.get_json(str(badge)):
            cached_officer = redis_cache.get_json(badge)
            if cached_officer == officer:
                continue

        # If officer is not in cache, add them to cache and publish to queue
        officer["work_history"] = "\r\n".join(officer["work_history"])
        redis_cache.set_json(badge, officer)
        redis_pub.publish("officers", json.dumps(officer))



        
if __name__ == "__main__":
    main()
    # schedule.every(1).days.do(main)

    # while True:
    #     print("Running main")
    #     schedule.run_pending()
    #     time.sleep(1)
