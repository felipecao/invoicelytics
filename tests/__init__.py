from faker import Faker
from faker.providers import lorem, internet, ssn, file

test_faker = Faker()
test_faker.add_provider(file)
test_faker.add_provider(internet)
test_faker.add_provider(lorem)
test_faker.add_provider(ssn)
