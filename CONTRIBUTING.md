# Contributing

All contributions are valued and welcomed, whether they come in the form of code, documentation, ideas or discussion.
While we have not applied a formal Code of Conduct to this repository, we require that all contributors
conduct themselves in a professional and respectful manner.

## Issues

The easiest way to contribute is through [Issues](https://github.com/vjayaramrh/assistedinstaller/issues). Feel free to take assignment
of or comment on an existing issue, or open a new issue making a suggestion or reporting a bug.

## Workflow

The required workflow for making a contribution is Fork-and-Pull. This is well documented elsewhere but to summarize:

1. Create a branch for the issue you are working on (see [Creating a branch to work on an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-a-branch-for-an-issue))
2. Clone/fetch the repo and switch to the new branch
3. Make code changes and test them (see [Testing](#testing) section)
4. Commit changes and submit a pull request (see [Commits and Pull Requests](#commits-and-pull-requests) section)

All contributions must have as much test coverage as possible and include relevant additions and changes to both
documentation and tooling. Once a change is implemented, tested, documented, and passing all checks then submit a pull
request for it to be reviewed.

## Testing

Each module requires an example playbook in the top-level directory of the repo that demonstrates usage and tests module
parameters. At a minimum, ensure that this example playbook executes without error and returns the expected results,
for example:

```
read -s OFFLINE_TOKEN # from https://console.redhat.com/openshift/token
ocm login --token=$OFFLINE_TOKEN
export AI_API_TOKEN=`ocm token`
ansible-playbook example.yml
```

All pull requests are automatically tested by a GitHub [workflow](https://github.com/vjayaramrh/assistedinstaller/blob/main/.github/workflows/test-module.yml).

Before submitting a pull request, you can test manually by running ansible-test on your work-in-progress branch, for example:

```
mkdir -p testing/ansible_collections/openshift_lab/
cp -pr devel/assistedinstaller/ testing/ansible_collections/openshift_lab/assisted_installer/
cd testing/ansible_collections/openshift_lab/assisted_installer/
virtualenv .ansible-test
source .ansible-test/bin/activate
pip install https://github.com/ansible/ansible/archive/devel.tar.gz --disable-pip-version-check
ansible-test sanity -v --docker --color --coverage
```

Address any errors reported and retest until ansible-test reports success.

## Commits and Pull Requests

A good commit does a *single* thing, does it completely, concisely, and describes *why*.

The commit message should explain both what is being changed and, in the case of anything non-obvious, why that change
was made. Commit messages are something that has been extensively written about so need not be discussed in more detail
here, but contributors should follow [these seven rules](https://chris.beams.io/posts/git-commit/#seven-rules) and keep
individual commits focussed.

A good pull request is the same; it also does a *single* thing, does it completely, and describes *why*. The difference
is that a Pull Request may contain one or more commits that together prepare for and deliver a feature.

Instructions on how to restructure commits to create a clear and understandable set of changes is outside the scope of
this document, but it's a useful skill and there are [many](https://thoughtbot.com/blog/autosquashing-git-commits)
[guides](https://git-scm.com/docs/git-rebase) and [approaches](https://nuclearsquid.com/writings/git-add/) for it.

Once your code changes have been committed and your branch has been pushed to the origin repo, [submit a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) for review.

## Peer Review and Merging

At least two maintainers must approve a pull request prior to merging. No self review is allowed. If your pull
request needs attention, please reach out to project [contributors](https://github.com/vjayaramrh/assistedinstaller/graphs/contributors) directly.

Contributors are asked to respond to queries and comments from reviewers in a timely manner in order to keep the review
process moving.

All contributors are strongly encouraged to review pull requests. Everyone is responsible for the quality of what is
produced, and review is also an excellent opportunity to learn.

## Style Guidelines

- Favor readability over brevity in both naming and structure
- Document the _why_ with comments, and the _what_ with clear code
- Follow the structure and guidelines in the [Developing modules](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html) section of the Ansible Developer Guide
- When in doubt, follow the [PEP 8](https://peps.python.org/pep-0008/) style guide
