Contributions to validations-libs follow guidelines largely similar
to those of other openstack projects.

If you're interested in contributing to the validations-libs project,
the following will help get you started:

   https://docs.openstack.org/infra/manual/developers.html

If you already have a good understanding of how the system works and your
OpenStack accounts are set up, you can skip to the development workflow
section of this documentation to learn how changes to OpenStack should be
submitted for review via the Gerrit tool:

   https://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

Validations are meant to verify functionality of tripleo systems.
Therefore a special care should be given to testing your code before submitting a review.

Branches and version management
===============================
Validation Framework project uses semantic versioning and derives names of stable branches
from the released minor versions. The latest minor version released is the only exception
as it is derived from the `master` branch.

Therefore, all code used by version 1.n.* of the project resides in `stable/1.n` branch,
and when version 1.(n+1) is released, new branch `stable/1.(n+1)` will be created.

By default, stable branches recieve only bug fixes and feature backports are decided on case basis
after all the necessary discussions and procedures have taken place.
