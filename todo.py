#!/usr/bin/env python3
""" lists and adds tasks to todoist """

import os
import sys
import todoist


def connect():
    """ Connect to todoist """
    # Get API Token for todoist
    api_file = open(os.path.expanduser("~/.config/todoist/api_key"), "r")
    api_key = api_file.read()
    api_file.close()

    # Connect to todoist
    api = todoist.TodoistAPI(api_key)
    api.sync()
    return api


def print_help():
    """ Prints out help """
    msg = "add [project] [task] - adds task to project\n"
    msg += "list - lists all projects and their items\n"
    msg += "list [project] - lists items associated with that project\n"
    msg += "projects - lists projects"
    print(msg)
    exit(0)


def get_proj_id(api, project):
    """ Takes the api object and a project name and returns its id """
    # Get ID for project if it exists
    for p in api.state['projects']:
        if p['name'].lower() == project.lower():
            project_id = p['id']
    try:
        return project_id
    except NameError:
        return None


def add_task(api, project_name, task):
    """ Takes a todoist api object, the project name, and the task and adds
    the task to todoist """

    project_id = get_proj_id(api, project_name)
    if not project_id:
        project_id = create_project(api, project_name)
    api.items.add(task, project_id)
    api.commit()
    print("Task added")


def create_project(api, name):
    """ Takes the api and the name of a project and creates it and returns
    the new project's id """
    api.projects.add(name)
    api.commit()
    print("Created Project: {}".format(name))

    return get_proj_id(api, name)


def list_all_tasks(api):
    """ Takes the api and Returns a list of all tasks """
    projects = {}
    tasks = {}
    for p in api.state['projects']:
        name = p['name']
        project_id = p['id']
        p[project_id] = name

    for item in api.state['items']:
        if item['is_deleted']:
            break
        if item['in_history']:
            break

        project_id = item['project_id']
        project_name = projects[project_id]
        content = item['content']
        if project_name in tasks:
            tasks[project_name].append(content)
        else:
            tasks[project_name] = [content]

    for p, tasks in tasks.items():
        for task in tasks:
            print("{} - {}".format(p, task))


def list_tasks(api, project):
    """ Takes the api and project name and returns the tasks associated with
    that project """
    tasks = []
    project_id = ''
    for p in api.state['projects']:
        if p['name'].lower() == project.lower():
            project_id = p['id']

    if not project_id:
        print("No project named {}".format(project))
        exit(0)
    for item in api.state['items']:
        if item['is_deleted']:
            break
        if item['in_history']:
            break

        if item['project_id'] == project_id:
            tasks.append(item['content'])

    print("\n".join(tasks))
    return


def list_projects(api):
    """ Takes the API object and prints a list of projects """
    projects = []
    for p in api.state['projects']:
        projects.append(p['name'])

    projects.sort(key=lambda y: y.lower())
    print("\n".join(projects))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
    API = connect()
    ACTION = sys.argv[1]

    if ACTION == 'add':
        if len(sys.argv) < 3:
            print_help()
        add_task(API, sys.argv[2], ' '.join(sys.argv[3:]))
    elif ACTION == 'list':
        if len(sys.argv) == 2:
            list_all_tasks(API)
        else:
            list_tasks(API, ' '.join(sys.argv[2:]))
    elif ACTION == 'projects':
        list_projects(API)
    else:
        print_help()
