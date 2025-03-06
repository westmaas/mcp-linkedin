from linkedin_api import Linkedin
from fastmcp import FastMCP
import os
import logging
import json

mcp = FastMCP("mcp-linkedin")
logger = logging.getLogger(__name__)

def get_client():
    return Linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD"), debug=True)


@mcp.tool()
def get_profile(public_id: str) -> str:
    """
    Get profile using public ID (the part after /in/ in profile URL)
    :param public_id: public ID of user (the part after /in/ in profile URL)
    :return: User Profile Details as json
    """
    client = get_client()
    try:
    # Get profile using public ID (the part after /in/ in profile URL)
        profile = client.get_profile(public_id=public_id)
    except Exception as e:
        logger.error(f"Error for {public_id}: {e}")
        return f"Error: {e}"
    
    profile_json = json.dumps(profile)
    return profile_json

@mcp.tool()
def get_feed_posts(limit: int = 10, offset: int = 0) -> str:
    """
    Retrieve LinkedIn feed posts.

    :return: List of feed post details
    """
    client = get_client()
    try:
        post_urns = client.get_feed_posts(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error: {e}"
    
    posts = ""
    for urn in post_urns:
        posts += f"Post by {urn['author_name']}: {urn['content']}\n"

    return posts

@mcp.tool()
def search_jobs(keywords: str, limit: int = 3, offset: int = 0, location: str = '') -> str:
    """
    Search for jobs on LinkedIn.
    
    :param keywords: Job search keywords
    :param limit: Maximum number of job results
    :param location: Optional location filter
    :return: List of job details
    """
    client = get_client()
    jobs = client.search_jobs(
        keywords=keywords,
        location_name=location,
        limit=limit,
        offset=offset,
    )
    job_results = ""
    for job in jobs:
        job_id = job["entityUrn"].split(":")[-1]
        job_data = client.get_job(job_id=job_id)

        job_title = job_data["title"]
        company_name = job_data["companyDetails"]["com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"]["companyResolutionResult"]["name"]
        job_description = job_data["description"]["text"]
        job_location = job_data["formattedLocation"]

        job_results += f"Job by {job_title} at {company_name} in {job_location}: {job_description}\n\n"

    return job_results

if __name__ == "__main__":
    print(search_jobs(keywords="data engineer", location="Jakarta", limit=2))
