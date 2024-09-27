import requests
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    """
    Django management command to check the remaining rate limit for a GitHub API token.
    """

    help = 'Check the remaining rate limit of the GitHub API for the provided token'

    def handle(self, *args, **kwargs):
        """
        The main method that sends a request to the GitHub API to get the rate limit status
        and prints the remaining requests and reset time.
        """
        token = settings.GITHUB_TOKEN  # Fetch GitHub token from settings
        headers = {"Authorization": f"token {token}"}

        url = "https://api.github.com/rate_limit"

        try:
            # Send a request to GitHub's rate limit API
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            rate_limit_data = response.json()

            # Extract relevant data for core API rate limits
            core_rate_limit = rate_limit_data.get('rate', {})
            remaining = core_rate_limit.get('remaining', 'Unknown')
            limit = core_rate_limit.get('limit', 'Unknown')
            reset_time = core_rate_limit.get('reset', 'Unknown')

            # Display the rate limit information
            self.stdout.write(self.style.SUCCESS(
                f"GitHub API Rate Limit: {remaining}/{limit} requests remaining"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"Rate limit will reset at: {reset_time} (UNIX timestamp)"
            ))

        except requests.exceptions.RequestException as e:
            # Handle any network or request errors
            self.stdout.write(self.style.ERROR(f"Error fetching rate limit: {e}"))
