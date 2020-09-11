# Upload 177
import os
import random
import shutil
import sys
import time

import matplotlib.pyplot as plt
import networkx as nx


def init():
    os.makedirs(os.path.join('.wit', 'images'), exist_ok=True)
    os.makedirs(os.path.join('.wit', 'staging_area'), exist_ok=True)
    with open(os.path.join(os.getcwd(), '.wit', 'activated.txt'), 'w') as file:
        file.write("master")


def find_closest_wit_folder(path):
    """

    :param path: the path we weant to locate the correct .wit path from
    :return: the path of the closest .wit folder. in case of no .wit folder will return None
    """
    while os.path.split(path)[1]:
        if os.path.isdir(os.path.join(path, '.wit')):
            return os.path.join(path, '.wit')
        path = os.path.split(path)[0]


def copy_file(source, dest):
    if os.path.isfile(source):
        shutil.copy2(source, dest)
    elif os.path.isdir(source):
        folder_name = os.path.split(source)[1]
        try:
            shutil.copytree(source, os.path.join(dest, folder_name))
        except FileExistsError:
            shutil.rmtree(os.path.join(dest, folder_name))
            shutil.copytree(source, os.path.join(dest, folder_name))


class WitFolderNotFound(FileNotFoundError):
    pass


def add():
    file_to_copy = os.path.join(os.getcwd(), sys.argv[2])
    if not os.path.exists(file_to_copy):
        print(f"{file_to_copy} is not exist")
        return None
    destenation = find_closest_wit_folder(os.getcwd())
    if destenation is None:
        raise WitFolderNotFound
    destenation = os.path.join(destenation, 'staging_area')
    contain_wit_folder = os.path.dirname(find_closest_wit_folder(os.getcwd()))
    full_path_to_create = file_to_copy.replace(contain_wit_folder, '', 1)
    created_folder = []
    while os.path.split(full_path_to_create)[1]:
        created_folder.append(os.path.split(full_path_to_create)[1])
        full_path_to_create = os.path.split(full_path_to_create)[0]
    created_folder.reverse()
    for folder in created_folder[:-1]:
        os.chdir(destenation)
        if not os.path.isdir(os.path.join(destenation, folder)):
            os.mkdir(folder)
            print(f'{folder} has created')
        destenation = os.path.join(destenation, folder)
    copy_file(file_to_copy, destenation)
    print(os.path.split(file_to_copy)[1], 'has been added')


used_commit_id = []


def generator_commit_id():
    valid_chars = '1234567890abcdef'
    while True:
        new_commit_id = ''
        for _ in range(40):
            new_commit_id += random.choice(valid_chars)
        if new_commit_id not in used_commit_id:
            used_commit_id.append(new_commit_id)
            yield new_commit_id


comit_id_generator = generator_commit_id()


def get_branch_commit(wit_folder, branch_to_get):
    with open(os.path.join(wit_folder, 'references.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    if branch_to_get not in content:
        return None
    return content[branch_to_get]


def get_head_commit(wit_path):
    return get_branch_commit(wit_path, "HEAD")


def create_text_from_content(data_dict):
    return_string = ""
    for key in data_dict:
        return_string += key + '=' + data_dict[key] + '\n'
    return return_string[:-1]


def set_brunch_commit(wit_folder, brunch, new_commit):
    with open(os.path.join(wit_folder, 'references.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    if brunch not in content:
        return None
    content[brunch] = new_commit
    with open(os.path.join(wit_folder, 'references.txt'), 'w') as file:
        file.write(create_text_from_content(content))


def set_head_commit(wit_folder, new_head):
    set_brunch_commit(wit_folder, 'HEAD', new_head)


def get_branch_list(wit_folder):
    with open(os.path.join(wit_folder, 'references.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    brunch_list = list(content.keys())
    brunch_list.remove("HEAD")
    return brunch_list


def commit():
    wit_folder = find_closest_wit_folder(os.getcwd())
    if wit_folder is None:
        raise WitFolderNotFound(".wit folder is not found")
    images_folder = os.path.join(wit_folder, 'images')
    os.chdir(images_folder)
    commit_id = next(comit_id_generator)
    try:
        message = sys.argv[2]
    except IndexError:
        message = "No message entered"
    if os.path.isfile(os.path.join(wit_folder, 'references.txt')):
        parent = get_head_commit(wit_folder)
    else:
        parent = "None"
    with open(os.path.join(images_folder, commit_id) + '.txt', 'a') as file:
        file.write(f"parent={parent}\ndate={time.asctime()}\nmessage={message}")
    staging_folder = os.path.join(wit_folder, 'staging_area')
    shutil.copytree(staging_folder, os.path.join(images_folder, commit_id))
    with open(os.path.join(wit_folder, 'activated.txt'), 'r') as file:
        activated = file.read()
    if os.path.isfile(os.path.join(wit_folder, 'references.txt')):
        if get_branch_commit(wit_folder, activated) == get_branch_commit(wit_folder, "HEAD"):
            set_brunch_commit(wit_folder, activated, commit_id)
        set_brunch_commit(wit_folder, "HEAD", commit_id)
    else:
        with open(os.path.join(wit_folder, 'references.txt'), 'w') as file:
            file.write('HEAD=' + commit_id + '\n' + activated + '=' + commit_id)

    print(f"{commit_id} has been created...")


def is_the_same_file(path1, path2):
    statu1 = os.stat(path1)
    status2 = os.stat(path2)
    if statu1[6] == status2[6] and statu1[8] == status2[8]:
        return True
    return False


def compare_files_from_two_dirs(dir1, dir2, before=""):
    not_exist_in_dir2 = []
    exist_but_different = []
    for file in os.listdir(dir1):
        path = os.path.join(dir1, file)
        if not os.path.exists(os.path.join(dir2, file)):
            not_exist_in_dir2.append(os.path.join(before, file))
        else:
            if os.path.isfile(path):
                if not is_the_same_file(path, os.path.join(dir2, file)):
                    exist_but_different.append(os.path.join(before, file))
            elif os.path.isdir(path):
                not_exist_in_dir2 += compare_files_from_two_dirs(path, os.path.join(dir2, file), os.path.join(before, file))[0]
                exist_but_different += compare_files_from_two_dirs(path, os.path.join(dir2, file), os.path.join(before, file))[1]
    return not_exist_in_dir2, exist_but_different


def status():
    status_dict = {}
    wit_folder = find_closest_wit_folder(os.getcwd())
    if wit_folder is None:
        raise WitFolderNotFound
    status_dict["Head:"] = get_head_commit(wit_folder)
    head_commit = get_head_commit(wit_folder)
    parent_folder = os.path.join(wit_folder, 'images', head_commit)
    staging_area = os.path.join(wit_folder, 'staging_area')
    compare_staging_paretnt = compare_files_from_two_dirs(staging_area, parent_folder)
    status_dict['changes_to_be_commited:'] = compare_staging_paretnt[1] + compare_staging_paretnt[0]
    compare_genuine_folder_staging_folder = compare_files_from_two_dirs(os.path.dirname(wit_folder), staging_area)
    compare_staging_to_genuine = compare_files_from_two_dirs(staging_area, os.path.dirname(wit_folder))
    status_dict['Changes not staged for commit:'] = compare_genuine_folder_staging_folder[1] + compare_staging_to_genuine[0]
    status_dict["Untracked files:"] = compare_genuine_folder_staging_folder[0]
    return status_dict


def print_status():
    print("STATUS:\n")
    status_dict = status()
    for key in status_dict:
        print(key)
        print(status_dict[key])


def checkout_file(file_to_checkout, commit_path):
    wit_folder = find_closest_wit_folder(file_to_checkout)
    path_from_commit = file_to_checkout.replace(commit_path, '', 1)[1:]
    os.chdir(os.path.dirname(wit_folder))
    if os.path.dirname(path_from_commit):
        os.makedirs(os.path.dirname(path_from_commit), exist_ok=True)
    destination = os.path.dirname(os.path.join(os.path.dirname(wit_folder), path_from_commit))
    if os.path.isfile(file_to_checkout):
        shutil.copy2(file_to_checkout, destination)
    if os.path.isdir(file_to_checkout):
        for file in os.listdir(file_to_checkout):
            print(os.path.join(file_to_checkout, file))
            checkout_file(os.path.join(file_to_checkout, file), commit_path)


def checkout():
    try:
        checkout_input = sys.argv[2]
    except IndexError:
        print("Must write commit id or brunch")
        return None
    wit_folder = find_closest_wit_folder(os.getcwd())
    if wit_folder is None:
        raise WitFolderNotFound
    with open(os.path.join(wit_folder, 'references.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    branch_list = list(content.keys())
    branch_list.remove("HEAD")
    commit_id = None
    if checkout_input in branch_list:
        commit_id = content[checkout_input]
        with open(os.path.join(wit_folder, 'activated.txt'), 'w') as file:
            file.write(checkout_input)
    if os.path.isdir(os.path.join(wit_folder, 'images', checkout_input)):
        commit_id = checkout_input
    if commit_id is None:
        print("Not such a brunch or commit exists")
        print("Exists Brunch:")
        print(branch_list)
        return None
    status_dict_values = list(status().values())
    if len(status_dict_values[1]) != 0:
        print("These Files are in staging area were not commited yet and some data might be lost")
        for file in status_dict_values[1]:
            print(file)
        print("Try commit to update these files and checkout again.")
        return None
    if len(status_dict_values[2]) != 0:
        print("These files were added to be commited but are different from original folder. some data might be lost")
        for file in status_dict_values[2]:
            print(file)
        print("Try add them again and commit so data wont be lost.")
        return None
    commit_path = os.path.join(wit_folder, 'images', commit_id)
    for file in os.listdir(commit_path):
        checkout_file(os.path.join(commit_path, file), commit_path)
    set_head_commit(wit_folder, commit_id)
    print("Checkout has been done...")
    shutil.rmtree(os.path.join(wit_folder, 'staging_area'))
    shutil.copytree(commit_path, os.path.join(wit_folder, 'staging_area'))


def get_parent(wit_folder, commit_id):
    commit_path = os.path.join(wit_folder, 'images', commit_id + '.txt')
    if not os.path.exists(commit_path):
        raise FileNotFoundError("The commit Id is wrong")
    with open(commit_path, 'r') as file:
        content = file.read()
        parent = content.splitlines()[0].split('=')[1]
    return parent


def get_edges(wit_folder, current_head):
    next_parent = get_parent(wit_folder, current_head)
    if next_parent == "None":
        return []
    if len(next_parent.split(',')) == 1:
        return [(current_head[:6], next_parent[:6])] + get_edges(wit_folder, next_parent)
    else:
        parents = next_parent.split(',')
        return [[(current_head[:6], parent[:6])] + get_edges(wit_folder, parent) for parent in parents]


def graph():
    wit_folder = find_closest_wit_folder(os.getcwd())
    if wit_folder is None:
        raise WitFolderNotFound("No wit folder has been found")
    head = get_head_commit(wit_folder)
    G = nx.DiGraph()
    edges = get_edges(wit_folder, head)
    while not isinstance(edges[0], tuple):
        new_list = []
        for lst in edges:
            for obj in lst:
                new_list.append(obj)
        edges = new_list
    print(edges)
    G.add_edges_from(edges)

    nx.draw_networkx(G, node_size=3500, with_labels=True)
    plt.draw()
    plt.show()


def help_func():
    print("""The functions you can use are:
    1.init
    2.add
    3.commit
    4.status
    5.graph
    6.branch
    7.merge
    9.commit""")


def branch():
    wit_folder = find_closest_wit_folder(os.getcwd())
    if wit_folder is None:
        raise WitFolderNotFound("No wit folder has been found")
    try:
        branch_name = sys.argv[2]
    except IndexError:
        print("Must add a name after using the brunch function")
    else:
        if not os.path.isfile(os.path.join(wit_folder, 'references.txt')):
            print("No commit has been done yet. must create a commit before use branch")
            return None
        with open(os.path.join(wit_folder, 'references.txt'), 'r') as file:
            content = dict(([line.split('=') for line in file.read().split('\n')]))
        if branch_name in content:
            raise ValueError("This brunch is already exist")
        with open(os.path.join(wit_folder, 'references.txt'), 'a') as file:
            file.write('\n' + branch_name + '=' + get_head_commit(wit_folder))
        print(branch_name + " branch has been created")


def add_parent(wit_folder, head, parent):
    with open(os.path.join(wit_folder, 'images', head + '.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    content['parent'] += f',{parent}'
    with open(os.path.join(wit_folder, 'images', head + '.txt'), 'w') as file:
        file.write(create_text_from_content(content))


def set_message(wit_folder, head, new_message):
    with open(os.path.join(wit_folder, 'images', head + '.txt'), 'r') as file:
        content = dict(([line.split('=') for line in file.read().split('\n')]))
    content['message'] = new_message
    with open(os.path.join(wit_folder, 'images', head + '.txt'), 'w') as file:
        file.write(create_text_from_content(content))


def merge():
    try:
        branch_name = sys.argv[2]
    except IndexError:
        print("Must write a branch after merge command")
        return None
    wit_folder = find_closest_wit_folder(os.getcwd())
    staging_folder = os.path.join(wit_folder, 'staging_area')
    if branch_name in get_branch_list(wit_folder):
        branch_folder = os.path.join(wit_folder, 'images', get_branch_commit(wit_folder, branch_name))
    else:
        print("This Brunch is not exist")
        return None
    status_dict_values = list(status().values())
    if len(status_dict_values[1]) != 0:
        print("These Files are in staging area were not commited yet and some data might be lost")
        for file in status_dict_values[1]:
            print(file)
        print("Try commit to update these files and checkout again.")
        return None
    if len(status_dict_values[2]) != 0:
        print("These files were added to be commited but are different from original folder. some data might be lost")
        for file in status_dict_values[2]:
            print(file)
        print("Try add them again and commit so data wont be lost.")
        return None
    for file in os.listdir(branch_folder):
        file_path = os.path.join(branch_folder, file)
        if os.path.isfile(file_path):
            shutil.copy2(file, staging_folder)
        if os.path.isdir(file_path):
            folder_name = os.path.split(file_path)[1]
            try:
                shutil.copytree(file_path, os.path.join(staging_folder, folder_name))
            except FileExistsError:
                shutil.rmtree(os.path.join(staging_folder, folder_name))
                shutil.copytree(file_path, os.path.join(staging_folder, folder_name))
    commit()
    print("Merge has been done")
    add_parent(wit_folder, get_head_commit(wit_folder), get_branch_commit(wit_folder, branch_name))
    set_message(wit_folder, get_head_commit(wit_folder), f"merged of {branch_name}")


func_dict = {'init': init,
             'add': add,
             'commit': commit,
             'status': print_status,
             'help': help_func,
             'checkout': checkout,
             'graph': graph,
             'branch': branch,
             'merge': merge}

try:
    to_function = func_dict[sys.argv[1]]
except IndexError:
    print("Must write a command. write help for commands list.")
except KeyError:
    print(f"{sys.argv[1]} is not a a valid command. write help for commands list.")
else:
    to_function()
