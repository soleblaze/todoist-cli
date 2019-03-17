""" Basic tests for todoistcli """
import json
import todoistcli


class api:
    """ Mock api """
    state = {
        "items": [
            {"id": 1, "project_id": 1, "content": "item 1", "is_archived": 0,
             "in_history": 0, "is_deleted": 0, "labels": [1]},
            {"id": 2, "project_id": 1, "content": "item 2", "is_archived": 0,
             "in_history": 0, "is_deleted": 0, "labels": [2]},
            {"id": 3, "project_id": 3, "content": "item 3", "is_archived": 0,
             "in_history": 0, "is_deleted": 0, "labels": []},
            {"id": 4, "project_id": 4, "content": "item 4", "is_archived": 1,
             "in_history": 0, "is_deleted": 0, "labels": []},
            {"id": 5, "project_id": 5, "content": "item 5", "is_archived": 0,
             "in_history": 1, "is_deleted": 0, "labels": []},
            {"id": 6, "project_id": 6, "content": "item 6", "is_archived": 0,
             "in_history": 0, "is_deleted": 1, "labels": []}
        ],
        "labels": [
            {"id": 1, "name": "label 1", "is_deleted": 0},
            {"id": 2, "name": "label 2", "is_deleted": 0},
            {"id": 3, "name": "label 3", "is_deleted": 0},
            {"id": 4, "name": "label 4", "is_deleted": 1}
        ],
        "projects": [
            {"id": 1, "name": "project 1", "is_archived": 0, "is_deleted": 0},
            {"id": 2, "name": "project 2", "is_archived": 0, "is_deleted": 0},
            {"id": 3, "name": "project 3", "is_archived": 0, "is_deleted": 0},
            {"id": 4, "name": "project 4", "is_archived": 1, "is_deleted": 0},
            {"id": 5, "name": "project 5", "is_archived": 0, "is_deleted": 1}
        ]
    }


def test_print_help(capsys):
    """ Verify that print_help prints out help """
    todoistcli.print_help()
    out, _ = capsys.readouterr()
    assert "add [project] [task] - adds task to project" in out


def test_print_formatted_output(capsys):
    """ Verify that format outputs correctly """
    todoistcli.print_formatted_output("test print")
    out, _ = capsys.readouterr()
    assert out == "test print\n"


def test_natural_sort():
    """ Validate that output is sorted naturally """
    initial_list = ["10", "11", "1", "14", "A", "d", "C", "b"]
    sorted_list = sorted(initial_list, key=todoistcli.natural_sort)
    assert sorted_list == ["1", "10", "11", "14", "A", "b", "C", "d"]


def test_get_projects():
    """ Validate get projects returns a list of projects """
    projects = todoistcli.get_projects(api)
    assert projects == {1: {"name": "project 1"},
                        2: {"name": "project 2"},
                        3: {"name": "project 3"}}


def test_get_labels():
    """ Validate get_labels returns a list of labels"""
    labels = todoistcli.get_labels(api)
    assert labels == {"label 1": 1,
                      "label 2": 2,
                      "label 3": 3}


def test_get_items():
    """ Validate get_items returns a list of items"""
    items = todoistcli.get_items(api)
    assert items == {1: {1: {'content': 'item 1', 'index': 1, "labels": [1]},
                         2: {'content': 'item 2', 'index': 2, "labels": [2]}},
                     3: {3: {'content': 'item 3', 'index': 3, "labels": []}}}


def test_save_state(tmpdir):
    """ Validate that save_state saves the current todoist state in the expected format """
    output = tmpdir.join('test_cache')
    test_data = 'tests/test_state.json'

    todoistcli.save_state(api.state['projects'], api.state['items'], api.state['labels'], output)

    fh = open(test_data)
    expected = json.load(fh)
    fh.close()

    fh = open(output)
    actual = json.load(fh)
    fh.close()

    assert actual == expected
