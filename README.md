# pytest-cloudist

pytest-cloudist is a pytest plugin to that distributes your tests to AWS EC2 machines with a minimum of fuss. It is a thin wrapper around [Meadowrun](https://meadowrun.io), which does the heavy lifting of starting EC2 instances and synchronizing environment and code.

## Installation

Assuming you already have an AWS account configured, install pytest-cloudist:

```
python -m pip install pytest-cloudist
```

And one-time install meadowrun into your AWS account:

```
meadowrun-manage-ec2 install
```

If you get stuck, for more information on configuring AWS and Meadowrun please visit https://docs.meadowrun.io/en/stable/tutorial/install/

Now the following command line arguments on `pytest` are available:

```
Distributed testing in the cloud using Meadowrun:
  --cloudist={test,file,no}
                        Set mode for distributing tests to workers.
                        test: send each test to a worker separately.
                        file: send each test file to a worker separately.
                        (default) no: run tests inprocess, don't distribute.
  --cd-tasks-per-worker-target=tasks_per_worker_target
                        The number of tasks to target per worker. This number determines whether individual tests or files are grouped and sent as a chunk to the test worker. Chunking is normally more efficient, but may affect load balancing and worsen the effect of stragglers.
  --cd-num-workers=num_workers
                        Number of workers to use for distributed testing.
  --cd-cpu-per-worker=logical_cpu_per_worker
                        The number of logical CPUs needed per worker.
  --cd-memory-per-worker=memory_gb_per_worker
                        The amount of memory (in GiB) needed per worker.
  --cd-interrupt-prob=INTERRUPTION_PROBABILITY_THRESHOLD
                        The estimated probability that spot instances are interrupted by AWS. Set to 0 for on-demand instances, which will be up to 10x more expensive.
  --cd-extra-files=EXTRA_FILES
                        Extra files to copy as to the remote machines, if needed. .py files on sys.path are copied automatically.
  --cd-init-command=INIT_COMMAND
                        Initialization command to run once per worker
```

## Usage

By default, pytest-cloudist is not activated, i.e. your tests run locally as normal. To enable pytest-cloudist, pass either `--cloudist test` or `--cloudist file` with any other options.

## Credits

The code and approach of pytest-cloudist, in terms of pytest integration, are heavily based on the code for [pytest-xdist](https://github.com/pytest-dev/pytest-xdist), and as a result it is also licensed as MIT.

