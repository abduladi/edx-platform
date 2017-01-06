"""
Command to add UUID for Instructor.
"""

import logging
import uuid

from django.core.management.base import BaseCommand
from xmodule.modulestore.django import modulestore

from openedx.core.djangoapps.models.course_details import CourseDetails
from django.contrib.auth.models import User


log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Example usage:
        $ ./manage.py cms add_instructor_ids --settings=devstack
    """
    help = 'Generates and stores course overview for one or more courses.'

    def handle(self, *args, **options):

        course_keys = [course.id for course in modulestore().get_course_summaries()]

        for key in course_keys:
            course_descriptor = CourseDetails.fetch(key)
            instructor_info = course_descriptor.instructor_info
            descriptor_json = course_descriptor.__dict__

            # Adding UUID in each instructor
            for instructor in instructor_info.get("instructors", []):
                if "UUID" not in instructor:
                    instructor["UUID"] = str(uuid.uuid4())

            # Update the course
            CourseDetails.update_from_json(
                key,
                descriptor_json,
                User.objects.get(username="lms_catalog_service_user")
            )

        # json = CourseDetails.fetch(course_keys[9]).__dict__
        # json["instructor_info"] = CourseDetails.fetch(course_keys[4]).instructor_info
        # print(json)
        #
        # print(CourseDetails.update_from_json(course_keys[9], json, User.objects.get(username="lms_catalog_service_user")))
        #
        # print(CourseDetails.fetch(course_keys[0]).instructor_info)
        # print(CourseDetails.fetch(course_keys[3]).instructor_info)
        #
        # #print(course_keys[2], course_keys[1])
        #

        # for index, key in enumerate(course_keys):
        #     print(index, key, CourseDetails.fetch(key).instructor_info)
