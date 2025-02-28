# Assisted Installer Ansible Module Unit Tests

## Running Unit Tests
`AI_API_TOKEN=test AI_PULL_SECRET=test python -m unittest discover tests/unit/`

## Design
A simple set of unit tests, currently covering clusters.py, written using the unittest framework, with guidance from https://docs.ansible.com/ansible/latest/dev_guide/testing_units_modules.html. The responses from the API are mocked using the `responses` library, and there are some known issues noted in the tests themselves. Parameterization is done in a somewhat naive way, so prints are added to make current tests more clear. This is a limitation of the way that Ansible suggests testing modules, which involes catching exceptions to correctly handle both normal and failed exit conditions. There are definitely improvements that can be made.