""" Basic tests for todoistcli """
import todoistcli


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
    """ Validate that output is sorted naturally"""
    initial_list = ["10", "11", "1", "14", "A", "d", "C", "b"]
    sorted_list = sorted(initial_list, key=todoistcli.natural_sort)
    assert sorted_list == ["1", "10", "11", "14", "A", "b", "C", "d"]
