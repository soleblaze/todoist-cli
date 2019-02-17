#!/usr/bin/env python3
""" lists and adds tasks to todoist """

import json
import os
import re
import sys
import todoist


def print_help():
    """ Prints out help """
    msg = "add [project] [task] - adds task to project\n"
    msg += "done [task index] - marks task as done\n"
    msg += "labels - lists labels\n"
    msg += "list - lists all projects and their items\n"
    msg += "list [label] - lists items associated with that label\n"
    msg += "list [project] - lists items associated with that project\n"
    msg += "projects - lists projects"
    print(msg)
    exit(0)


def natural_sort(s, nsre=re.compile('([0-9]+)')):
    """ Used as a key in sorted to naturally sort numbers in strings """
    return [int(text) if text.isdigit() else text.lower()
            for text in nsre.split(s)]


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


def get_projects(api):
    """ Get a list of projects and a dict for the useful info """
    projects = {}
    for project in api.state['projects']:
        if project['is_deleted']:
            continue
        if project['is_archived']:
            continue
        projects[project['id']] = {
            "name": project['name']
        }
    return projects


def get_labels(api):
    """ Get a list of projects and a dict for the useful info """
    labels = {}
    for label in api.state['labels']:
        if label['is_deleted']:
            continue
        labels[label['name']] = label['id']
    return labels


def get_items(api):
    """ Get a list of projects and a dict for the useful info """
    items = {}
    for item in api.state['items']:
        if item['is_deleted']:
            continue
        if item['in_history']:
            continue
        if item['is_archived']:
            continue

        if item['project_id'] not in items:
            items[item['project_id']] = {}
        items[item['project_id']][item['id']] = {
            "content": item['content'],
            "labels": item['labels']
        }

        index = 1
        for proj_id in items:
            for id in items[proj_id]:
                items[proj_id][id].update({"index": index})
                index += 1
    return items


def save_state(projects, items, labels):
    state = {
        "projects": projects,
        "items": items,
        "labels": labels
    }
    fh = open(os.path.expanduser("~/.config/todoist/cache"), "w")
    fh.write(json.dumps(state))
    fh.close()
    return True


def load_state():
    with open(os.path.expanduser("~/.config/todoist/cache"), "r") as f:
        data = json.load(f)
    return data


def items_cache():
    return load_state()['items']


def projects_cache():
    return load_state()['projects']


def sync(api):
    projects = get_projects(api)
    items = get_items(api)
    labels = get_labels(api)
    save_state(projects, items, labels)
    return {"projects": projects, "items": items, "labels": labels}


def list_projects(api):
    projects = sync(api)['projects']
    output = []
    for id in projects:
        output.append(projects[id]['name'])

    print('\n'.join(sorted(output, key=natural_sort)))
    return True


def list_labels(api):
    labels = sync(api)['labels']

    print('\n'.join(sorted(labels, key=natural_sort)))
    return True


def list_items(api):
    if len(sys.argv) == 2:
        list_items_all(api)
    elif len(sys.argv) == 3:
        print_help()
    elif sys.argv[2].lower() == 'project':
        list_items_project(api, ' '.join(sys.argv[3:]))
    elif sys.argv[2].lower() == 'label':
        list_items_label(api, ' '.join(sys.argv[3:]))
    else:
        print_help()


def list_items_project(api, project):
    data = sync(api)
    items = data['items']
    projects = data['projects']
    labels = data['labels']
    proj_ids = []
    output = []

    for id in projects:
        if project.lower() in projects[id]['name'].lower():
            proj_ids.append(id)

    if not proj_ids:
        print("No project named {}".format(project))
        exit(0)

    for proj_id in proj_ids:
        for id in items[proj_id]:
            temp_labels = []
            try:
                project_name = projects[proj_id]['name']
                content = items[proj_id][id]['content']
                index = items[proj_id][id]['index']

                for label in items[proj_id][id]['labels']:
                    temp_labels.append('@' + labels[label])

            except KeyError:
                continue

            i_labels = ' '.join(temp_labels)

            output.append(f"[{index}] {project_name} - {content} {i_labels}")

    print('\n'.join(sorted(output, key=natural_sort)))
    return True


def list_items_label(api, label):
    data = sync(api)
    items = data['items']
    projects = data['projects']
    labels = data['labels']
    label_ids = []
    output = []

    for name in labels:
        if label.lower() in name.lower():
            label_ids.append(labels[name])

    if not label_ids:
        print("No label named {}".format(label))
        exit(0)

    for label_id in label_ids:
        for proj_id in items:
            for item_id in items[proj_id]:
                if label_id in items[proj_id][item_id]['labels']:
                    temp_labels = []

                    try:
                        project_name = projects[proj_id]['name']
                        content = items[proj_id][item_id]['content']
                        index = items[proj_id][item_id]['index']

                        for label in items[proj_id][item_id]['labels']:
                            name = ' '.join([l for l in labels if labels[l] == label])
                            temp_labels.append('@' + name)

                    except KeyError:
                        continue

                    i_labels = ' '.join(temp_labels)

                    output.append(f"[{index}] {project_name} - {content} {i_labels}")

    print('\n'.join(sorted(output, key=natural_sort)))
    return True


def list_items_all(api):
    data = sync(api)
    items = data['items']
    labels = data['labels']
    projects = data['projects']
    output = []
    for proj_id in items:
        for id in items[proj_id]:
            temp_labels = []
            try:
                project_name = projects[proj_id]['name']
                content = items[proj_id][id]['content']
                index = items[proj_id][id]['index']

                for label in items[proj_id][id]['labels']:
                    temp_labels.append('@' + labels[label])

            except KeyError:
                continue

            i_labels = ' '.join(temp_labels)

            output.append(f"[{index}] {project_name} - {content} {i_labels}")

    print('\n'.join(sorted(output, key=natural_sort)))
    return True


def get_proj_id(api, project):
    """ Takes the api object and a project name and returns its id """
    # Get ID for project if it exists
    projects = sync(api)['projects']

    for id in projects:
        if projects[id]['name'].lower() == project.lower():
            project_id = id
    try:
        return project_id
    except NameError:
        return None


def create_project(api, name):
    """ Takes the api and the name of a project and creates it and returns
    the new project's id """
    api.projects.add(name)
    api.commit()
    print("Created Project: {}".format(name))

    return get_proj_id(api, name)


def add_item(api):
    """ Takes a todoist api object, the project name, and the task and adds
    the task to todoist """

    if len(sys.argv) < 4:
        print_help()
        exit(0)

    project_name = sys.argv[2]
    task = ' '.join(sys.argv[3:])

    project_id = get_proj_id(api, project_name)

    if not project_id:
        project_id = create_project(api, project_name)
    api.items.add(task, project_id)
    api.commit()
    print("Task added")


def done(api):
    """ Takes a todoist api object, the project name, and the task and adds
    the task to todoist """

    if len(sys.argv) != 3:
        print_help()
        exit(0)

    index = int(sys.argv[2])
    items = items_cache()

    for proj_id in items:
        for id in items[proj_id]:
            if items[proj_id][id]['index'] == index:
                item_id = id
                content = items[proj_id][id]['content']
                break

    api.items.complete([item_id])
    api.commit()
    print(f"Marking [{index}] {content} as done")

    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
    API = connect()
    ACTION = sys.argv[1]

    ACTIONS = {
        "sync": lambda: sync(API),
        "projects": lambda: list_projects(API),
        "list": lambda: list_items(API),
        "label": lambda: list_labels(API),
        "add": lambda: add_item(API),
        "done": lambda: done(API)
    }

    ACTIONS.get(ACTION, lambda: print_help())()
