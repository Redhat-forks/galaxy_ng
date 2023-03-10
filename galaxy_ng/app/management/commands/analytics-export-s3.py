import boto3
import traceback
import logging

from django.core.management.base import BaseCommand
from galaxy_ng.app.management.commands.analytics.collector import Collector
from galaxy_ng.app.management.commands.analytics import galaxy_collector
from django.utils.timezone import now, timedelta
import os

logger = logging.getLogger("analytics")


class Command(BaseCommand):
    """Django management command to export collections data to s3 bucket"""

    def handle(self, *args, **options):
        """Handle command"""

        collector = Collector(
            collector_module=galaxy_collector,
            collection_type="dry-run",
            logger=logger,
        )

        tar_files = collector.gather(
            since=now() - timedelta(days=8), until=now() - timedelta(days=1)
        )

        errors = False

        for tar_file in tar_files:
            try:
                self.write_file_to_s3(tar_file)
            except:
                errors = True
                traceback.print_exc()

        print("Completed " + ("successfully" if errors is False else "with errors"))

    def write_file_to_s3(self, file_name):
        """
        Copies data to s3 bucket file
        """

        with open(file_name, "rb"):

            # Upload the file
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("aws_access_key_id"),
                aws_secret_access_key=os.getenv("aws_secret_access_key"),
                region_name=os.getenv("aws_region"),
            )
            response = s3_client.upload_file(
                file_name, os.getenv("aws_bucket"), os.path.basename(file_name).split("/")[-1]
            )

            return response


if __name__ == "__main__":
    cmd = Command()
    cmd.handle()
