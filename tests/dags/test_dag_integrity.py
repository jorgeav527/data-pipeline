import pytest
from airflow.models import DagBag
from airflow.utils.dag_cycle_tester import check_cycle


@pytest.fixture(scope="module")
def dagbag():
    return DagBag()


def test_dag_integrity(dagbag):
    """
    Check that all of the DAGs are in good health.

    It tests the following:
    - input: dagbag from airflow.models.
    - output: assert if no imported errors exist within the tasks.
    - output: assert the dag id name, the existence of tasks, or if the dag is not None in each dag.
    - output: assert in each dag if no cycle infinite forloop exists.
    """
    assert (
        len(dagbag.import_errors) == 0
    ), f"DAG import failures: {dagbag.import_errors}"
    for dag_id, dag in dagbag.dags.items():
        assert dag is not None
        assert dag.dag_id == dag_id
        assert len(dag.tasks) > 0
        assert check_cycle(dag) is None, f"{dag_id} has a cycle"
        # errors = dag.test()
        # assert len(errors) == 0  # check that there are no errors in the DAG definition
