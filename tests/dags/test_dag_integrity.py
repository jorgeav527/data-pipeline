"""Test the validity of all DAGs"""

from airflow.models import DagBag


def test_dagbag():
    """Validate DAG files using Airflow's models DagBag.
    - Check if the tasks have required arguments.
    - Check if DAG ids are unique.
    - Check if DAG have no rounded cycles.
    """
    dag_bag = DagBag(include_examples=False)
    assert not dag_bag.import_errors

    for dag_id, dag in dag_bag.dags.items():
        error_msg = f"{dag_id} in {dag.full_filepath} has no tags"
        assert dag.tags, error_msg
