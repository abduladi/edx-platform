"""
Command to add UUID for Instructor.
"""

import uuid
import logging


from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.models.course_details import CourseDetails


log = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Example usage:
    ./manage.py cms add_instructor_ids --username <username>
    --course_keys <key1> [<key2> <key3> ...] --settings=devstack
    """
    help = './manage.py cms add_instructor_ids --username <username>' \
           ' --course_keys <key1> [<key2> <key3> ...] --settings=devstack'

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '--course_keys',
            nargs='+',
            help='Enter one or more course keys',
            required=True
        )

        parser.add_argument(
            '--username',
            required=True,
            help='Enter an existing username',
        )

    def handle(self, *args, **options):

        username = options['username']
        course_keys = options['course_keys']

        for key in course_keys:
            course_key = CourseKey.from_string(key)
            course_descriptor = CourseDetails.fetch(course_key)

            # Adding UUID in each instructor
            for instructor in course_descriptor.instructor_info.get("instructors", []):
                if "uuid" not in instructor:
                    instructor["uuid"] = str(uuid.uuid4())

            # Updating the course
            CourseDetails.update_from_json(
                course_key,
                course_descriptor.__dict__,
                User.objects.get(username=username)
            )
