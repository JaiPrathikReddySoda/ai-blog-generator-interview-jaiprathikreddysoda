import random
import logging

def get_seo_data(keyword):
    """
    Generate mock SEO metadata for a given keyword.
    This simulates realistic SEO data for demonstration/testing.

    Args:
        keyword (str): The keyword to analyze.

    Returns:
        dict: Simulated metrics including:
            - search_volume: Estimated monthly searches (int)
            - keyword_difficulty: Relative difficulty to rank (int, 0-100)
            - avg_cpc: Estimated average cost-per-click (float)
    """
    keyword = keyword.lower()
    logging.info(f"[SEO] Generating SEO data for: {keyword}")

    seo_data = {
        "search_volume": random.randint(3000, 20000),       # Simulate traffic range
        "keyword_difficulty": random.randint(20, 70),       # Arbitrary SEO difficulty
        "avg_cpc": round(random.uniform(0.5, 3.5), 2)       # Simulate CPC in USD
    }

    return seo_data
