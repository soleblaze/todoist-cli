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
    todoistcli.print_formatted_output(["line 1", "line 2"])
    out, _ = capsys.readouterr()
    assert out == "line 1\nline 2\n"


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

    projects = todoistcli.get_projects(api)
    items = todoistcli.get_items(api)
    labels = todoistcli.get_labels(api)

    todoistcli.save_state(projects, items, labels, output)

    fh = open(test_data)
    expected = json.load(fh)
    fh.close()

    fh = open(output)
    actual = json.load(fh)
    fh.close()

    assert actual == expected


def test_load_state():
    """ Validate that load_state loads the current todoist state in the expected format """
    test_data = 'tests/test_state.json'

    actual = todoistcli.load_state(test_data)

    assert actual["projects"] == {"1": {"name": "project 1"},
                                  "2": {"name": "project 2"},
                                  "3": {"name": "project 3"}}
    assert actual["items"] == {"1": {"1": {"content": "item 1", "index": 1, "labels": [1]},
                                     "2": {"content": "item 2", "index": 2, "labels": [2]}},
                               "3": {"3": {"content": "item 3", "index": 3, "labels": []}}}

    assert actual["labels"] == {"label 1": 1, "label 2": 2, "label 3": 3}


def test_items_cache():
    """ Validate that items_cache returns the items expected """
    test_data = 'tests/test_state.json'
    actual = todoistcli.items_cache(test_data)

    assert actual == {"1": {"1": {"content": "item 1", "index": 1, "labels": [1]},
                            "2": {"content": "item 2", "index": 2, "labels": [2]}},
                      "3": {"3": {"content": "item 3", "index": 3, "labels": []}}}



def test_projects_cache():
    """ Validate that projects_cache returns the projects expected """
    test_data = 'tests/test_state.json'

    actual = todoistcli.projects_cache(test_data)
    assert actual == {"1": {"name": "project 1"},
                      "2": {"name": "project 2"},
                      "3": {"name": "project 3"}}



def test_labels_cache():
    """ Validate that labels_cache returns the labels expected """
    test_data = 'tests/test_state.json'

    actual = todoistcli.labels_cache(test_data)
    assert actual == {"label 1": 1, "label 2": 2, "label 3": 3}


def test_sync(tmpdir):
    """ Validate that sync returns the proper data """
    output = tmpdir.join('test_cache')

    actual = todoistcli.sync(api, output)

    projects = {1: {"name": "project 1"},
                2: {"name": "project 2"},
                3: {"name": "project 3"}}

    items = {1: {1: {'content': 'item 1', 'index': 1, "labels": [1]},
                 2: {'content': 'item 2', 'index': 2, "labels": [2]}},
             3: {3: {'content': 'item 3', 'index': 3, "labels": []}}}

    labels = {"label 1": 1,
              "label 2": 2,
              "label 3": 3}

    assert actual['items'] == items
    assert actual['labels'] == labels
    assert actual['projects'] == projects


def test_list_projects(tmpdir):
    """ Validate that list_projects returns the proper projects """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_projects(api, output)

    assert actual == ["project 1 (2)", "project 2 (0)", "project 3 (1)"]


def test_list_labels(tmpdir):
    """ Validate that list_labels returns the proper labels"""

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_labels(api, output)

    assert actual == ["label 1 (1)", "label 2 (1)", "label 3 (0)"]


def test_list_items_project_success(tmpdir):
    """ Validates all items associated with project 1 are outputted """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_project(api, "project 1", output)

    assert actual == ["[1] project 1 - item 1 @label 1", "[2] project 1 - item 2 @label 2"]


def test_list_items_project_match(tmpdir):
    """ Validates all items that matches proj in project name are outputted """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_project(api, "proj", output)

    assert actual == ["[1] project 1 - item 1 @label 1",
                      "[2] project 1 - item 2 @label 2",
                      "[3] project 3 - item 3"]


def test_list_items_project_failure(tmpdir):
    """ Returns an empty array """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_project(api, "invalid", output)

    assert actual == []


def test_list_items_label_success(tmpdir):
    """ Validates all items associated with label 1 are outputted """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_label(api, "label 1", output)

    assert actual == ["[1] project 1 - item 1 @label 1"]


def test_list_items_label_failure(tmpdir):
    """ Returns an empty array """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_label(api, "invalid", output)

    assert actual == []


def test_list_items_all(tmpdir):
    """ Validates all items are outputted """

    output = tmpdir.join('test_cache')
    actual = todoistcli.list_items_all(api, output)

    assert actual == ["[1] project 1 - item 1 @label 1",
                      "[2] project 1 - item 2 @label 2",
                      "[3] project 3 - item 3 "]


def test_list_projects_cache():
    """ Validates all items are outputted """
    test_data = 'tests/test_state.json'

    actual = todoistcli.list_cache_projects(test_data)

    assert actual == ["project 1", "project 2", "project 3"]
