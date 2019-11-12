import string
import random

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))

def new_test_project_name():
  project_name = f"test-pyatlas-project-{ random_string() }"
  return project_name

