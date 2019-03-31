"""
validate.py

Workhorse function that validates an OLX course
"""
import os
from edx_xml_clean.errorstore import ErrorStore
from edx_xml_clean.loader import load_course, load_policy
from edx_xml_clean.parser.policy import find_url_names, merge_policy, validate_grading_policy
from edx_xml_clean.parser.validators import GlobalValidator
from edx_xml_clean.parser.longvalidators import LongValidator
from edx_xml_clean.utils import traverse

def validate(filename, steps=0, quiet=True, ignore=None):
    """
    Validate an OLX course

    :param filename: Location of course xml file or directory
    :param steps: Number of validation steps to take (0 = all)
    :param quiet: Output information to the console
    :param ignore: List of errors to ignore
    :return: course object, errorstore object
    """
    # Create an error store
    if ignore is None:
        ignore = []
    errorstore = ErrorStore(ignore)

    # Validation Step #1: Load the course
    if os.path.isdir(filename):
        directory = os.path.join(filename)
        file = "course.xml"
    else:
        directory, file = os.path.split(filename)
    course = load_course(directory, file, errorstore, quiet)
    if not course:
        return None, errorstore
    if steps == 1:
        return course, errorstore

    # Validation Step #2: Load the policy files
    policy, grading_policy = load_policy(directory, course, errorstore)
    if steps == 2:
        return course, errorstore

    # Validation Step #3: Construct a dictionary of url_names
    url_names = find_url_names(course, errorstore)
    if steps == 3:
        return course, errorstore

    # Validation Step #4: Merge policy data into object attributes
    merge_policy(policy, url_names, errorstore)
    if steps == 4:
        return course, errorstore

    # Validation Step #5: Validate grading policy
    validate_grading_policy(grading_policy, course, errorstore)
    if steps == 5:
        return course, errorstore

    # Validation Step #6: Have every object validate itself
    for edxobj in traverse(course):
        edxobj.validate(errorstore)
    if steps == 6:
        return course, errorstore

    # Validation Step #7: Parse the course for global errors
    for validator in GlobalValidator.validators():
        validator(course, errorstore, url_names)
    if steps == 7:
        return course, errorstore

    # Validation Step #8: Parse the course for long global errors
    for validator in LongValidator.validators():
        validator(course, errorstore, url_names)
    return course, errorstore