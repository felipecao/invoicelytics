from faker import Faker
from faker.providers import lorem, internet, ssn, file, misc
from unittest.mock import patch  # noqa: E402

test_faker = Faker()
test_faker.add_provider(file)
test_faker.add_provider(internet)
test_faker.add_provider(lorem)
test_faker.add_provider(misc)
test_faker.add_provider(ssn)

patch("flask_login.login_required", lambda x: x).start()
