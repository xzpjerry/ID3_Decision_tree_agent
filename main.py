from math import log
from collections import Counter

# SAMPLE_FILE_NAME = "waiting.csv"
SAMPLE_FILE_NAME = "golf.csv"
# Sources File Handler layer


def csv_handler(filename):
    # csv to recognizable data type
    num_attributes = 0
    num_labels = 0
    attributes = []
    attributes_vals = []
    labels = []
    with open(filename, 'r') as f:
        # assume the 1st column is the id, and the last column is the label
        attributes = f.readline().strip().split(',')[1:-1]
        num_attributes = len(attributes)
        for line in f.readlines():
            raw_attributes_val = line.strip().split(',')[1:]
            attributes_val = {}
            for i in range(num_attributes):
                attributes_val[attributes[i]] = raw_attributes_val[i]
            label = raw_attributes_val.pop()
            attributes_vals.append(attributes_val)
            labels.append(label)
            num_labels += 1
    return (attributes, attributes_vals, labels, num_attributes, num_labels)

# Samples Splicer layer


def get_splited_input(FROM_INPUTS, with_attribute, of_value):
    # A helper function is used to split
    # the input regarding to their attributes
    # and attributes' values into the standard format
    old_attributes = FROM_INPUTS[0]
    old_attributes_vals = FROM_INPUTS[1]
    old_labels = FROM_INPUTS[2]

    new_attributes = [x for x in old_attributes if x != with_attribute]
    new_num_attributes = FROM_INPUTS[3] - 1
    new_attributes_vals = []
    new_labels = []
    new_num_labels = 0

    if type(of_value) != type([]):
        counter = 0
        for bundle in old_attributes_vals:
            if bundle[with_attribute] == of_value:
                new_attributes_vals.append(bundle)
                new_labels.append(old_labels[counter])
                new_num_labels += 1

            counter += 1
    else:
        counter = 0
        threshold = of_value[0]
        for bundle in old_attributes_vals:
            if float(bundle[with_attribute]) > threshold:
                new_attributes_vals.append(bundle)
                new_labels.append(old_labels[counter])
                new_num_labels += 1

            counter += 1

    return (new_attributes, new_attributes_vals, new_labels, new_num_attributes, new_num_labels)

# Computation layer


def get_entropy(INPUTS):
    labels = INPUTS[2]
    count_dict = Counter(labels)
    total_len = INPUTS[4]
    rslt = 0
    for key, val in count_dict.items():
        px = val / total_len
        rslt += (-px * log(px, 2))
    return rslt


def get_info_gain_ratio(INPUTS, attribute, possible_attributes_vals, with_threshold=None):
    this_attributes_entropy = 0
    split_info = 0.0
    num_labels = INPUTS[4]
    curr_entropy = get_entropy(INPUTS)

    if with_threshold == None:
        for possible_val in possible_attributes_vals:
            splited_input = get_splited_input(INPUTS, attribute, possible_val)
            p = splited_input[4] / num_labels
            # print(splited_input)

            split_info += (-p * log(p, 2))

            entropy_here = p * get_entropy(splited_input)
            this_attributes_entropy += entropy_here
    else:
        splited_input = get_splited_input(INPUTS, attribute, with_threshold)
        # print(splited_input)
        p = splited_input[4] / num_labels

        split_info += (-p * log(p, 2))

        entropy_here = p * get_entropy(splited_input)
        this_attributes_entropy += entropy_here

    if split_info == 0.0:
        return 0
    info_gain = curr_entropy - this_attributes_entropy
    info_gain_ratio = info_gain / split_info
    return info_gain_ratio


def get_best_attribute(INPUTS):
    attributes = INPUTS[0]
    attributes_vals = INPUTS[1]

    curr_max_info_gain_ratio = -1

    rslt = None
    for attribute in attributes:
        the_threshold = None
        # get unique possible values
        possible_attributes_vals = [x[attribute] for x in attributes_vals]
        possible_attributes_vals = list(set(possible_attributes_vals))
        is_continuous = ":continuous" in attribute
        info_gain_ratio = -1
        if not is_continuous:
            info_gain_ratio = get_info_gain_ratio(
                INPUTS, attribute, possible_attributes_vals)
            if info_gain_ratio > curr_max_info_gain_ratio:
                curr_max_info_gain_ratio = info_gain_ratio
                rslt = (attribute, possible_attributes_vals, the_threshold)
        else:
            possible_attributes_vals = list(
                map(float, possible_attributes_vals))
            possible_attributes_vals.sort()
            num_vals = len(possible_attributes_vals)
            for i in range(num_vals - 1):
                this_val = possible_attributes_vals[i]
                next_val = possible_attributes_vals[i + 1]
                if this_val != next_val:
                    the_threshold = (this_val + next_val) / 2
                    info_gain_ratio = get_info_gain_ratio(
                        INPUTS, attribute, possible_attributes_vals, [the_threshold])
                    if info_gain_ratio > curr_max_info_gain_ratio:
                        curr_max_info_gain_ratio = info_gain_ratio
                        rslt = (attribute, possible_attributes_vals, [the_threshold])

    return rslt

# Tree Generator layer


def get_tree(INPUTS):
    rslt_tree = None
    attempt = get_best_attribute(INPUTS)
    if not attempt:
        return rslt_tree
    attribute, possible_attributes_vals, the_threshold = attempt
    # print(attempt)
    # Non-continuous
    if the_threshold == None:
        labels = INPUTS[2]
        if labels.count(labels[0]) == INPUTS[-1]:  # It's pure now.
            return labels[0]
        rslt_tree = {attribute: {}}
        for possible_attributes_val in possible_attributes_vals:
            splited_input = get_splited_input(
                INPUTS, attribute, possible_attributes_val)
            rslt_tree[attribute][possible_attributes_val] = get_tree(
                splited_input)
    else:
        rslt_tree = {attribute+">"+str(the_threshold): {}}
        print(rslt_tree)
        for possible_attributes_val in possible_attributes_vals:
            splited_input = get_splited_input(
                INPUTS, attribute, the_threshold)
            # print(splited_input)
            rslt_tree[attribute][possible_attributes_val] = get_tree(
                splited_input)
    return rslt_tree


if __name__ == "__main__":
    INPUT = csv_handler(SAMPLE_FILE_NAME)
    # print(INPUT)
    modal = get_tree(INPUT)
    '''
    With this sample, the modal would look like:
    {'Pat': {
        'SOME': 'T', 
        'NONE': 'F', 
        'FULL': {
            'Price': {
                '$$$': 'F', 
                '$': {
                    'Est': {
                        '10~30': 'T', 
                        '>60': 'F', 
                        '30~60': {
                            'Bar': {
                                'T': 'T', 
                                'F': 'F'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    # Using pydot we can easily visulize the tree
    # Credits
    # https://stackoverflow.com/questions/13688410/dictionary-object-to-decision-tree-in-pydot

    import pydot

    def draw(parent_name, child_name):
        edge = pydot.Edge(parent_name, child_name)
        graph.add_edge(edge)

    def visit(node, parent=None):
        for k, v in node.items():
            if isinstance(v, dict):
                # We start with the root node whose parent is None
                # we don't want to graph the None node
                if parent:
                    draw(parent, k)
                visit(v, k)
            else:
                draw(parent, k)
                # drawing the label using a distinct name
                draw(k, v)

    graph = pydot.Dot(graph_type='graph')
    visit(modal)
    graph.write_png('example1_graph.png')
